const API = "http://127.0.0.1:5000";

//  AUTH GUARD 
const token = sessionStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}

const role = sessionStorage.getItem("role");
const adminLink = document.getElementById("admin-link");

if (role === "admin" && adminLink) {
    adminLink.classList.remove("hidden");
}

// ─── AUTH HEADERS 
function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

// CHECK IF TOKEN IS EXPIRED 
function isTokenExpired(token) {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    } catch (error) {
        return true;
    }
}

// AUTO LOGOUT IF TOKEN EXPIRED 
function checkTokenAndLogout() {
    const token = sessionStorage.getItem("token");
    if (!token || isTokenExpired(token)) {
        sessionStorage.clear();
        window.location.href = "login.html";
    }
}


function handle401() {
    sessionStorage.clear();
    window.location.href = "login.html";
}

async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);

    if (response.status === 401) {
        handle401();
        throw new Error("Session expired. Redirecting to login.");
    }

    return response;
}



//  USER INFO 
const userEmail = sessionStorage.getItem("email");
if (userEmail) {
    document.getElementById("user-email").innerText = userEmail;
}

// ─── USER INFO + LOGOUT 

document.getElementById("btn-logout").addEventListener("click", () => {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("role");
    sessionStorage.removeItem("email");
    window.location.href = "login.html";
});



//  LOAD ALL EXPENSES ON PAGE OPEN 
window.addEventListener("DOMContentLoaded", () => {
    checkTokenAndLogout();
    setInterval(checkTokenAndLogout, 60000);
    loadExpenses();
    loadDashboard();
    loadCharts();        
});

// ─── DOM ELEMENTS 
const expenseForm = document.getElementById("expense-form");
const expenseBody = document.getElementById("expense-body");
const searchBtn   = document.querySelector(".search-btn");
const resetBtn    = document.querySelector(".reset-btn");


// ─── CHART INSTANCES 

let barChart  = null;
let pieChart  = null;
let lineChart = null;

// ─── LOAD ALL CHARTS 

async function loadCharts() {
    await loadCategoryChart();
    await loadTimeChart();
}

async function loadCategoryChart() {
    try {
        const response = await apiFetch(`${API}/expenses/categories/summary`, {
    headers: authHeaders()});
        const result   = await response.json();
        const data     = result.data;

        // Extract labels and values from the data
        const labels = data.map(item => item[0]);
        const values = data.map(item => item[1]);

        // Colors for each category
        const colors = [
            "#3B82F6",  
            "#2C3E7A",  
            "#16A34A",  
            "#DC2626",  
            "#F59E0B",  
            "#8B5CF6",  
            "#EC4899",  
            "#14B8A6",  
        ];

        // ── BAR CHART 
        const barCtx = document.getElementById("categoryBarChart").getContext("2d");

        if (barChart) barChart.destroy();

        barChart = new Chart(barCtx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Amount Spent ($)",
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => `$${value}`
                        }}}
            }
        });

        // ── PIE CHART ─
        const pieCtx = document.getElementById("categoryPieChart").getContext("2d");

        if (pieChart) pieChart.destroy();

        pieChart = new Chart(pieCtx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: "#FFFFFF"
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            font: { size: 11 },
                            padding: 12
                        }
                    }}}
        });

    } catch (error) {
        console.error("Category chart error:", error);
    }
}



async function loadTimeChart() {
    try {
        const response = await apiFetch(`${API}/expenses`, {
    headers: authHeaders()});
        const results = await response.json();

        // Group expenses by date and sum amounts per date
        const dateMap = {};

        if (!results.success || !Array.isArray(results.data)) {
            return;
        }

        if (results.data.length === 0) {
            if (lineChart) lineChart.destroy();
            return;
        }

        results.data.forEach(expense => {
            const date = expense.date || "Unknown";
            if (dateMap[date]) {
                dateMap[date] += expense.amount;
            } else {
                dateMap[date] = expense.amount;
            }
        });

        // Sort dates chronologically
        const sortedDates = Object.keys(dateMap).sort();
        const amounts     = sortedDates.map(date => dateMap[date]);


        // ── LINE CHART 
        const lineCtx = document.getElementById("timeLineChart").getContext("2d");

        if (lineChart) lineChart.destroy();

        lineChart = new Chart(lineCtx, {
            type: "line",
            data: {
                labels: sortedDates,
                datasets: [{
                    label: "Daily Spending ($)",
                    data: amounts,
                    borderColor: "#3B82F6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    borderWidth: 2,
                    pointBackgroundColor: "#2C3E7A",
                    pointRadius: 5,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => `$${value}`
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Time chart error:", error);
    }
}



// ─── SHOW MESSAGE 
function showMessage(message, type) {
    const box = document.getElementById("message-box");
    box.innerText        = message;
    box.style.display    = "block";
    box.style.color      = type === "success" ? "#16A34A" : "#DC2626";
    box.style.backgroundColor = type === "success" ? "#F0FDF4" : "#FEF2F2";
    box.style.border     = type === "success" 
                           ? "1px solid #BBF7D0" 
                           : "1px solid #FECACA";

    setTimeout(() => {
        box.style.display = "none";
        box.innerText     = "";
    }, 4000);
}


function formatMoney(value) {
    return `$${parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })}`;
}



async function loadExpenses() {
    try {
        const response = await apiFetch(`${API}/expenses`, {
            headers: authHeaders()
        });

        const result = await response.json();

        expenseBody.innerHTML = "";

        if (result.success) {
            result.data.forEach(expense => {
                addExpenseToTable(expense);
            });
        }

    } catch (error) {
        console.error("Failed to load expenses:", error);
    }
}



// ─── ADD EXPENSE 
expenseForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const expense = {
        name:     document.getElementById("name").value.trim(),
        amount:   document.getElementById("amount").value,
        category: document.getElementById("category").value.trim(),
        date:     new Date().toLocaleDateString()
    };

    try {
        const response = await apiFetch(`${API}/expenses`, {
            method:  "POST",
            headers: authHeaders(),
            body:    JSON.stringify(expense)
        });

        const data = await response.json();

        if (response.ok && data.success) {
            addExpenseToTable(data.expense);
            expenseForm.reset();
            loadDashboard();
            showMessage(data.message, "success");
        } else {
            showMessage(data.message, "error");
        }

    } catch (error) {
        console.error("Error:", error);
    }
});

// ─── ADD ROW TO TABLE ──
function addExpenseToTable(expense) {
    const row = document.createElement("tr");
    row.setAttribute("data-id", expense.id);

    const nameCell = document.createElement("td");
    nameCell.textContent = expense.name;

    const amountCell = document.createElement("td");
    amountCell.className = "amount";
    amountCell.textContent = formatMoney(expense.amount);

    const categoryCell = document.createElement("td");
    categoryCell.textContent = expense.category;

    const dateCell = document.createElement("td");
    dateCell.textContent = expense.date || "—";

    const actionCell = document.createElement("td");

    const updateButton = document.createElement("button");
    updateButton.className = "btn-update";
    updateButton.dataset.id = expense.id;
    updateButton.textContent = "Update";

    const deleteButton = document.createElement("button");
    deleteButton.className = "btn-delete";
    deleteButton.dataset.id = expense.id;
    deleteButton.textContent = "Delete";

    actionCell.appendChild(updateButton);
    actionCell.appendChild(deleteButton);

    row.appendChild(nameCell);
    row.appendChild(amountCell);
    row.appendChild(categoryCell);
    row.appendChild(dateCell);
    row.appendChild(actionCell);

    expenseBody.appendChild(row);
}

// ─── EVENT DELEGATION (UPDATE + DELETE) ────
expenseBody.addEventListener("click", (event) => {
    const target = event.target;

    if (target.classList.contains("btn-delete")) {
        handleDelete(target.dataset.id, target);
    }

    if (target.classList.contains("btn-update")) {
        handleUpdateClick(target.dataset.id, target);  
    }
});

// ─── DELETE ────
async function handleDelete(id, button) {
    const confirmed = confirm(`Are you sure you want to delete this expense? "${id}"?`);
    if (!confirmed) return;

    try {
        const response = await apiFetch(`${API}/expenses/${id}`, {
            method: "DELETE",
            headers: authHeaders()
        });

        const data = await response.json();

        if (data.success) {
            button.closest("tr").remove();
            loadDashboard();
            loadCharts(); 
            loadExpenses();
            showMessage(data.message, "success");
        } else {
            showMessage(data.message, "error");
        }

    } catch (error) {
        console.error(error);
    }
}

// ─── UPDATE: OPEN FORM ──
function handleUpdateClick( id,button) {
    const row      = button.closest("tr");
    const cells    = row.querySelectorAll("td");

    document.getElementById("update-id").value       = id;
    document.getElementById("update-name").value     = cells[0].innerText;
    document.getElementById("update-amount").value   = parseFloat(cells[1].innerText.replace(/[$,]/g, ""));
    document.getElementById("update-category").value = cells[2].innerText;
    document.getElementById("update-section").classList.remove("hidden");
    document.getElementById("update-name").focus();
}

// ─── UPDATE: CONFIRM ───
document.getElementById("btn-confirm-update").addEventListener("click", async () => {
    const id       = document.getElementById("update-id").value.trim();
    const name     = document.getElementById("update-name").value.trim();
    const amount   = parseFloat(document.getElementById("update-amount").value);
    const category = document.getElementById("update-category").value.trim();

    if (!id || !name || isNaN(amount) || amount <= 0 || !category) {
        showMessage("Please fill in all fields correctly.", "error");
        return;
    }

    try {
        const response = await apiFetch(`${API}/expenses/${id}`, {
            method:  "PUT",
            headers: authHeaders(),
            body:    JSON.stringify({ name, amount, category })
        });

        const data = await response.json();

        if (data.success) {
            const row = expenseBody.querySelector(`tr[data-id="${id}"]`);
            if (row) {
                const cells    = row.querySelectorAll("td");
                cells[0].innerText = name;
                cells[1].innerText = formatMoney(amount);
                cells[2].innerText = category;
            }
            closeUpdateForm();
            loadDashboard();
            showMessage(data.message, "success");
        } else {
            showMessage(data.message, "error");
        }

    } catch (error) {
        console.error("Update error:", error);
    }
});

// UPDATE: CANCEL 

document.getElementById("btn-cancel-update").addEventListener("click", closeUpdateForm);

function closeUpdateForm() {
    document.getElementById("update-section").classList.add("hidden");
    document.getElementById("update-id").value       = "";
    document.getElementById("update-name").value     = "";
    document.getElementById("update-amount").value   = "";
    document.getElementById("update-category").value = "";
}

// ─── DASHBOARD ─────
async function loadDashboard() {
    try {
        const totalRes   = await apiFetch(`${API}/expenses/total`, { headers: authHeaders() });
        const totalData  = await totalRes.json();

        if(!totalData.data || totalData.data.length===0){
           document.getElementById("total-expense").innerText ="N/A" 
        }
        else{
            document.getElementById("total-expense").innerText = formatMoney(totalData.data);
        }
        

        const countRes   = await apiFetch(`${API}/expenses/count`, { headers: authHeaders() });
        const countData  = await countRes.json();
        document.getElementById("expense-count").innerText = countData.data;

        const avgRes     = await apiFetch(`${API}/expenses/average`, { headers: authHeaders() });
        const avgData    = await avgRes.json();

        if(!avgData.data || avgData.data.length===0){
            document.getElementById("average-expense").innerText = "N/A"
        }
        else{
            document.getElementById("average-expense").innerText = formatMoney(avgData.data);
        }
        

        const minmaxRes  = await apiFetch(`${API}/expenses/minmax`, { headers: authHeaders() });
        const minmaxData = await minmaxRes.json();
        const rows = minmaxData.data;

        if (!rows || rows.length === 0) {
            document.getElementById("highest-expense").innerText = "N/A";
            document.getElementById("lowest-expense").innerText = "N/A";

        } else if (rows.length === 1) {
            document.getElementById("highest-expense").innerText =
                `${rows[0][0]}: ${formatMoney(rows[0][1])}`;
            document.getElementById("lowest-expense").innerText =
                `${rows[0][0]}: ${formatMoney(rows[0][1])}`;
        } else {
            document.getElementById("highest-expense").innerText =
                `${rows[0][0]}: ${formatMoney(rows[0][1])}`;
            document.getElementById("lowest-expense").innerText =
                `${rows[1][0]}: ${formatMoney(rows[1][1])}`;
        }
        

        const catRes     = await apiFetch(`${API}/expenses/categories/summary`, { headers: authHeaders() });
        const catData    = await catRes.json();
        const categoryBox = document.getElementById("category-summary");


        categoryBox.innerHTML = "";
        catData.data.forEach(item => {
            const div = document.createElement("div");
            div.innerText = `${item[0]} : ${formatMoney(item[1])}`;
            categoryBox.appendChild(div);
        });

        loadCharts();

    } catch (error) {
        console.error("Dashboard error:", error);
    }   
}


// ─── SEARCH ──────────
async function searchExpense() {
    const name = document.getElementById("search-input").value.trim();

    if (!name) {
        showMessage("Enter a name to search.", "error");
        return;}

    try {
        const response = await apiFetch(
            `${API}/expenses/search?name=${encodeURIComponent(name)}`,
            {
                headers: authHeaders()
            });

        const result = await response.json();

        expenseBody.innerHTML = "";

        if (!result.success) {
            showMessage(result.message, "error");
            return;
        }

        result.data.forEach(expense => {
            addExpenseToTable(expense);
        });

    } catch (error) {
        console.error("Search error:", error);
    }
}



searchBtn.addEventListener("click", searchExpense);
resetBtn.addEventListener("click", loadExpenses);




async function filterByCategory() {
    const userinput = document.getElementById("filter-input").value.trim();

    if (!userinput) {
        showMessage("Enter a category to filter.", "error");
        return;
    }

    try {
        const response = await apiFetch(
            `${API}/expenses/filter?category=${encodeURIComponent(userinput)}`,
            {
                headers: authHeaders()
            }
        );

        const result = await response.json();

        expenseBody.innerHTML = "";

        if (!result.success) {
            showMessage(result.message || "Filter failed", "error");
            return;
        }

        if (!result.data || result.data.length === 0) {
            showMessage("No expenses found", "error");
            return;
        }

        result.data.forEach((expense) => {
            addExpenseToTable(expense);
        });
        
        


    } catch (error) {
        console.error("filter error:", error);
        showMessage("Connection error. Try again later.", "error");
    }
}


const filterBtn = document.querySelector(".filter-btn");
filterBtn.addEventListener("click", filterByCategory);




