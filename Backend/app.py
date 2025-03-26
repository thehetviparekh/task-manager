from flask import Flask, request, jsonify
from flask_cors import CORS # type: ignore
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)
CORS(app)

def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        email TEXT,
                        password TEXT)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        title TEXT,
                        completed INTEGER DEFAULT 0)""")
        conn.commit()
init_db()

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (data['username'], data['email'], data['password']))
        conn.commit()
    return jsonify({"message": "User registered"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? AND password = ?", (data['email'], data['password']))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401
        token = create_access_token(identity=user[0])
    return jsonify({"token": token})

@app.route("/tasks", methods=["GET", "POST"])
@jwt_required()
def tasks():
    user_id = get_jwt_identity()
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        if request.method == "POST":
            data = request.json
            cursor.execute("INSERT INTO tasks (user_id, title) VALUES (?, ?)", (user_id, data['title']))
            conn.commit()
            return jsonify({"message": "Task added"})
        else:
            cursor.execute("SELECT id, title, completed FROM tasks WHERE user_id = ?", (user_id,))
            tasks = cursor.fetchall()
            return jsonify([{ "id": t[0], "title": t[1], "completed": bool(t[2]) } for t in tasks])

@app.route("/tasks/<int:task_id>", methods=["PUT", "DELETE"])
@jwt_required()
def update_delete_task(task_id):
    user_id = get_jwt_identity()
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        if request.method == "PUT":
            data = request.json
            cursor.execute("UPDATE tasks SET title = ?, completed = ? WHERE id = ? AND user_id = ?",
                           (data['title'], data['completed'], task_id, user_id))
            conn.commit()
            return jsonify({"message": "Task updated"})
        else:
            cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
            conn.commit()
            return jsonify({"message": "Task deleted"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)