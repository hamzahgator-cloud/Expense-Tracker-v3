const API = "http://127.0.0.1:5000";

function showAuthMessage(message, type) {
    const box = document.getElementById("auth-message");
    box.innerText     = message;
    box.style.color   = type === "success" ? "green" : "red";
    box.style.marginBottom = "12px";
}

async function apiFetch(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new Error("Connection error. Please try again.");
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
            (response.status === 429 && "Too many attempts. Please wait a moment and try again.") ||
            (response.status >= 500 && "Server error. Try again later.") ||
            "Something went wrong.";

        throw new Error(message);
    }

    return response;
}


window.addEventListener("DOMContentLoaded", () => {

    //  PASSWORD VISIBILITY TOGGLE 
    function setupEyeToggle(toggleId, inputId) {
        const toggle = document.getElementById(toggleId);
        const input  = document.getElementById(inputId);

        if (toggle && input) {
            toggle.addEventListener("click", () => {
                if (input.type === "password") {
                    input.type   = "text";
                    toggle.innerText = "🙈";
                } else {
                    input.type   = "password";
                    toggle.innerText = "👁";
                }
            });
        }
    }


    // Register &Login page toggles
    setupEyeToggle("toggle-password", "password");
    setupEyeToggle("toggle-confirm",  "confirm-password");


        // ─── REGISTER 
 
const registerBtn = document.getElementById("btn-register");

if (registerBtn) {
    registerBtn.addEventListener("click", async (event) => {
        event.preventDefault();
    event.stopPropagation();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm-password").value;

        if (!email || !password || !confirmPassword) {
            showAuthMessage("Please fill in all fields", "error");
            return;
        }

        if (password !== confirmPassword) {
            showAuthMessage("Passwords do not match,try again", "error");
            return;
        }

        if (password.length < 8) {
            showAuthMessage("Password must be at least 8 characters", "error");
            return;
        }

        try {
            const response = await apiFetch(`${API}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

           if (data.success) {
            sessionStorage.setItem("pendingVerificationEmail", email);
            window.location.href = `verify.html?email=${encodeURIComponent(email)}`;
            return;

            } else {
                showAuthMessage(data.message || "Registration failed", "error");
            }

        } catch (error) {
            showAuthMessage(error.message, "error");
        }
    });
}


    // LOGIN
   const loginBtn = document.getElementById("btn-login");
    if (loginBtn) {
        loginBtn.addEventListener("click", async () => {
            const email    = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;

            if (!email || !password) {
                showAuthMessage("Please fill in all fields", "error");
                return;
            }

            try {
                const response = await apiFetch(`${API}/auth/login`, {
                    method:  "POST",
                    headers: { "Content-Type": "application/json" },
                    body:    JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (data.success) {
                    sessionStorage.setItem("token", data.token);
                    sessionStorage.setItem("role",  data.role);
                    sessionStorage.setItem("email", email);

                if (data.role==="admin"){
                window.location.href = "admin.html";
                }

                else{
                    window.location.href = "index.html";
                }


               } else if (data.needs_verification) {
                sessionStorage.setItem("pendingVerificationEmail", email);
                window.location.href = `verify.html?email=${encodeURIComponent(email)}`;
                return;
                }

            else {
                showAuthMessage(data.message || "Login failed", "error");
            }

            } catch (error) {
            showAuthMessage(error.message, "error");
            }
        });
    }

});


