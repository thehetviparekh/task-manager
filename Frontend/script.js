async function addTask() {
    const taskTitle = document.getElementById("taskInput").value;
    const token = localStorage.getItem("token");
    if (!token) return alert("Please log in");
    const res = await fetch("http://localhost:5000/tasks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ title: taskTitle })
    });
    const data = await res.json();
    if (res.ok) {
        fetchTasks();
    } else {
        alert(data.message);
    }
}

async function fetchTasks() {
    const token = localStorage.getItem("token");
    const res = await fetch("http://localhost:5000/tasks", {
        headers: { "Authorization": "Bearer " + token }
    });
    const tasks = await res.json();
    const taskList = document.getElementById("taskList");
    taskList.innerHTML = "";
    tasks.forEach(task => {
        const li = document.createElement("li");
        li.textContent = task.title;
        taskList.appendChild(li);
    });
}

document.addEventListener("DOMContentLoaded", fetchTasks);
