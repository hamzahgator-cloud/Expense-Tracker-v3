const API = "http://127.0.0.1:5000";

const token = sessionStorage.getItem("token");
const role = sessionStorage.getItem("role");
const email = sessionStorage.getItem("email");

if (!token || role !== "admin") {
    window.location.href = "login.html";
}


function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

function showMessage(message, type) {
    const box = document.getElementById("message-box");
    if (!box) return;
    box.innerText = message;
    box.style.display = "block";
    box.style.color = type === "success" ? "green" : "red";
    setTimeout(() => {
        box.style.display = "none";
        box.innerText = "";
    }, 4000);
}

function formatMoney(value) {
    const num = Number(value || 0);
    return `$${num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}


async function apiFetch(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new Error("Connection error. Please try again.");
    }

    if (response.status === 401) {
        sessionStorage.clear();
        window.location.href = "login.html";
        throw new Error("Unauthorized");
    }

    if (!response.ok) {
        let data = null;

        try {
            data = await response.json();
        } catch (error) {
            data = null;
        }

        const message =
        (response.status < 500 && data && data.message) ||
        (response.status === 403 && "Access denied.") ||
        (response.status === 404 && "Not found.") ||
        (response.status === 429 && "Too many requests. Try again later.") ||
        (response.status >= 500 && "Server error. Try again later.") ||
        "Something went wrong.";

        throw new Error(message);
    }

    return response;
}


document.getElementById("admin-email").textContent = email || "";
document.getElementById("btn-logout").addEventListener("click", () => {
    sessionStorage.clear();
    window.location.href = "login.html";
});

async function loadSummary() {
    const [usersRes, summaryRes] = await Promise.all([
        apiFetch(`${API}/admin/users/count`, { headers: authHeaders() }),
        apiFetch(`${API}/admin/summary`, { headers: authHeaders() })
    ]);

    const usersData = await usersRes.json();
    const summaryData = await summaryRes.json();

    document.getElementById("total-users").textContent =
        usersData.data ?? "—";

    if (summaryData.success && summaryData.data) {
        document.getElementById("total-expenses").textContent =
            summaryData.data.total_expenses ?? "—";
        document.getElementById("total-amount").textContent =
            formatMoney(summaryData.data.total_amount);
        document.getElementById("average-amount").textContent =
            formatMoney(summaryData.data.average_amount);
    }
}

async function loadUsers() {
    const response = await apiFetch(`${API}/admin/users`, {
        headers: authHeaders()
    });
    const result = await response.json();
    const body = document.getElementById("users-body");
    body.innerHTML = "";

    if (!result.success || !result.data) {
        showMessage(result.message || "Could not load users", "error");
        return;
    }

    result.data.forEach((user) => {
        const row = document.createElement("tr");
        row.setAttribute("data-id", user.id);

        const idcell = document.createElement("td");
        idcell.textContent = user.id;
    
        const emailcell = document.createElement("td");
        emailcell.textContent = user.email;

        const rolecell = document.createElement("td");
        rolecell.textContent = user.role;

        const verifiedcell = document.createElement("td");
        verifiedcell.textContent = user.is_verified ? "Yes" : "No";

        const createdatcell = document.createElement("td");
        createdatcell.textContent = user.created_at.slice(0, 10);

        const activecell = document.createElement("td");
        activecell.textContent = user.is_active ? "Active" : "Not active";


        const actioncell = document.createElement("td");



if (user.role !== "admin") {
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "btn-delete";
    deleteBtn.textContent = "Delete";
    deleteBtn.addEventListener("click", () => deleteUser(user.id, user.email));
    actioncell.appendChild(deleteBtn);

    if (user.is_active) {
        const deactivateBtn = document.createElement("button");
        deactivateBtn.className = "btn-deactivate";
        deactivateBtn.textContent = "Deactivate";
        deactivateBtn.addEventListener("click", () => deactivateUser(user.id, user.email));
        actioncell.appendChild(deactivateBtn);
    } else {
        const activateBtn = document.createElement("button");
        activateBtn.className = "btn-activate";
        activateBtn.textContent = "Activate";
        activateBtn.addEventListener("click", () => activateUser(user.id, user.email));
        actioncell.appendChild(activateBtn);
    }
} else {
    actioncell.textContent = "—";
}


row.appendChild(idcell);
row.appendChild(emailcell);
row.appendChild(rolecell);
row.appendChild(verifiedcell);
row.appendChild(createdatcell);
row.appendChild(activecell);
row.appendChild(actioncell);

body.appendChild(row);
    });
}



async function deleteUser(userId, userEmail) {
    const ok = confirm(`Delete user "${userEmail}"?`);
    if (!ok) return;

    try {
        const response = await apiFetch(`${API}/admin/users/${userId}`, {
            method: "DELETE",
            headers: authHeaders()
        });

        const result = await response.json();

        if (result.success) {
            showMessage(result.message, "success");
            await loadUsers();
            await loadSummary();
        } else {
            showMessage(result.message || "Delete failed", "error");
        }

    } catch (error) {
    if (error.message === "Unauthorized") return;
    showMessage(error.message, "error");
    }
}


async function deactivateUser(userId, userEmail) {
    const ok = confirm(`Deactivate user "${userEmail}"?`);
    if (!ok) return;

    try{
        const response = await apiFetch(`${API}/admin/users/${userId}/deactivate`, {
            method: "PATCH",
            headers: authHeaders()
        });

        const result = await response.json();

        if (result.success) {
            showMessage(result.message, "success");
            await loadUsers();
            await loadSummary();
        } else {
            showMessage(result.message || "Deactivation failed", "error");
        }
        
    } catch (error) {
    if (error.message === "Unauthorized") return;
    showMessage(error.message, "error");
    }
}

async function activateUser(userId, userEmail) {
    const ok = confirm(`Activate user "${userEmail}"?`);
    if (!ok) return;

    try{
        const response = await apiFetch(`${API}/admin/users/${userId}/activate`, {
            method: "PATCH",
            headers: authHeaders()
        });

        const result = await response.json();

        if (result.success) {
            showMessage(result.message, "success");
            await loadUsers();
            await loadSummary();
        } else {
            showMessage(result.message || "Activation failed", "error");
        }
        
    } catch (error) {
    if (error.message === "Unauthorized") return;
    showMessage(error.message, "error");
    }
    }
    

window.addEventListener("DOMContentLoaded", async () => {
    try {
        await loadSummary();
        await loadUsers();

    } catch (error) {
    if (error.message === "Unauthorized") return;
    showMessage(error.message, "error");
    }
});