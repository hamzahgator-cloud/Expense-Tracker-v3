const API = "http://127.0.0.1:5000";

const token = sessionStorage.getItem("token");
const role = sessionStorage.getItem("role");
const email = sessionStorage.getItem("email");

if (!token) {
    window.location.href = "login.html";
}

if (role !== "admin") {
    window.location.href = "index.html";
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
    const response = await fetch(url, options);
    if (response.status === 401 || response.status === 403) {
        sessionStorage.clear();
        window.location.href = "login.html";
        throw new Error("Unauthorized");
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

    const response = await apiFetch(`${API}/admin/users/${userId}`, {
        method: "DELETE",
        headers: authHeaders()
    });
    const result = await response.json();

    if (result.success) {
        showMessage(result.message, "success");
        loadUsers();
        loadSummary();
    } else {
        showMessage(result.message || "Delete failed", "error");
    }
}


async function deactivateUser(userId, userEmail) {
    const ok = confirm(`Deactivate user "${userEmail}"?`);
    if (!ok) return;

    const response = await apiFetch(`${API}/admin/users/${userId}/deactivate`, {
        method: "PATCH",
        headers: authHeaders()
    });

    const result = await response.json();

    if (result.success) {
        showMessage(result.message, "success");
        loadUsers();
        loadSummary();
    } else {
        showMessage(result.message || "Deactivation failed", "error");
    }
}

async function activateUser(userId, userEmail) {
    const ok = confirm(`Activate user "${userEmail}"?`);
    if (!ok) return;

    const response = await apiFetch(`${API}/admin/users/${userId}/activate`, {
        method: "PATCH",
        headers: authHeaders()
    });
    const result = await response.json();

    if (result.success) {
        showMessage(result.message, "success");
        loadUsers();
        loadSummary();
    } else {
        showMessage(result.message || "Activation failed", "error");
    }
}
   

window.addEventListener("DOMContentLoaded", async () => {
    try {
        await loadSummary();
        await loadUsers();
    } catch (error) {
        console.error("Admin load error:", error);
    }
});