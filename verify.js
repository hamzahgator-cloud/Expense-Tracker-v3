const API = "http://127.0.0.1:5000";

function showAuthMessage(message, type) {
    const box = document.getElementById("auth-message");
    if (!box) return;
    box.innerText = message;
    box.style.color = type === "success" ? "green" : "red";
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
    const params = new URLSearchParams(window.location.search);
    const emailFromUrl = params.get("email");

    let pendingVerificationEmail =
        emailFromUrl || sessionStorage.getItem("pendingVerificationEmail");

    if (!pendingVerificationEmail) {
        showAuthMessage("No email to verify. Please register or login again.", "error");
        return;
    }

    // keep it available
    sessionStorage.setItem("pendingVerificationEmail", pendingVerificationEmail);

    const subtitle = document.getElementById("verify-subtitle");
    if (subtitle) {
        subtitle.textContent = `Enter the 6-digit code sent to ${pendingVerificationEmail}`;
    }

    // VERIFY
    const verifyBtn = document.getElementById("btn-verify-otp");
    if (verifyBtn) {
        verifyBtn.addEventListener("click", async () => {
            const otp = document.getElementById("otp-input").value.trim();

            if (!otp) {
                showAuthMessage("Enter the code from your email", "error");
                return;
            }

            try {
                const response = await apiFetch(`${API}/auth/verify-otp`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: pendingVerificationEmail,
                        otp: otp
                    })
                });

                const data = await response.json();

                if (data.success) {
                    sessionStorage.removeItem("pendingVerificationEmail");
                    showAuthMessage("Email verified! Redirecting to login...", "success");
                    setTimeout(() => {
                        window.location.href = "login.html";
                    }, 1000);
                } else {
                    showAuthMessage(data.message || "Verification failed", "error");
                }

            } catch (error) {
                showAuthMessage(error.message, "error");
            }
        });
    }

    // RESEND
    const resendBtn = document.getElementById("btn-resend-otp");
    if (resendBtn) {
        resendBtn.addEventListener("click", async (event) => {
            event.preventDefault();

            try {
                const response = await apiFetch(`${API}/auth/resend-otp`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: pendingVerificationEmail
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showAuthMessage("New code sent. Check your email.", "success");
                } else {
                    showAuthMessage(data.message || "Could not resend code", "error");
                }
            } catch (error) {
                showAuthMessage(error.message, "error");
            }
        });
    }
});