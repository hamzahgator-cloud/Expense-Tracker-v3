from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import bcrypt
import sqlite3
import secrets
import hashlib
from datetime import timedelta, timezone,datetime
import re
import os
import requests
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)

from extensions import limiter

auth = Blueprint("auth", __name__)

MAX_EMAIL_LENGTH = 254
MAX_PASSWORD_LENGTH = 128
OTP_LENGTH = 6
OTP_VALID_MINUTES = 10

EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID", "").strip()
EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID", "").strip()
EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY", "").strip()
EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY", "").strip()



DB_PATH = os.path.join(BASE_DIR, "expense.db")

def generate_otp():
    """Generate a random 6-digit numeric OTP as a string, e.g. '042917'."""
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


def hash_otp(otp):
    """
    OTPs .
    """
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def otp_expiry_timestamp():
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_VALID_MINUTES)
    return expires_at.isoformat()


def is_otp_expired(expires_at_str):
    if not expires_at_str:
        return True
    expires_at = datetime.fromisoformat(expires_at_str)
    return datetime.now(timezone.utc) > expires_at

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn



def send_otp_email(email, otp):
    if not all([EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, EMAILJS_PUBLIC_KEY, EMAILJS_PRIVATE_KEY]):
        print("EmailJS keys are missing in .env")
        return False

    url = "https://api.emailjs.com/api/v1.0/email/send"

    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "accessToken": EMAILJS_PRIVATE_KEY,
        "template_params": {
            "to_email": email,
            "otp_code": otp
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        print("EmailJS STATUS:", response.status_code)
        print("EmailJS RESPONSE:", response.text)

        return response.status_code == 200

    except requests.exceptions.RequestException as error:
        print("EmailJS CONNECTION ERROR:", error)
        return False


    

def users_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',is_verified INTEGER NOT NULL DEFAULT 0,
            otp_hash TEXT,
            otp_expires_at TEXT,
            created_at TEXT NOT NULL,
            deleted_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()



def strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "OK"


def valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


@auth.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():

    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Request must be JSON"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON data"
        }), 400
    
    
    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Email and password must be text"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password required"
        }), 400



    if len(email) > MAX_EMAIL_LENGTH:
        return jsonify({
            "success": False,
            "message": "Email address is too long"
        }), 400

    if not valid_email(email):
            return jsonify({
                        "success": False,
                        "message": "Email or password is invalid"
                    }), 400

    if len(password) > MAX_PASSWORD_LENGTH:
        return jsonify({
            "success": False,
            "message": "Password is too long"
        }), 400

    correct_password, message = strong_password(password)
    if not correct_password:
        return jsonify({"success": False, "message": message}), 400

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt()).decode("utf-8")


    otp = generate_otp()
    otp_hash = hash_otp(otp)
    otp_expires_at = otp_expiry_timestamp()
    created_at = datetime.now(timezone.utc).isoformat()

    # Save to database
    try:

        conn = get_db()

        conn.execute(
            """INSERT INTO users
            (email, password_hash, is_verified, otp_hash, otp_expires_at,created_at)
            VALUES (?, ?, 0, ?, ?,?)""",
            (email, password_hash, otp_hash, otp_expires_at, created_at)
        )

        conn.commit()
        conn.close()

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 400


    # Send OTP directly from backend
    email_sent = send_otp_email(email, otp)

    if not email_sent:
        # Remove the newly-created account if email sending failed
        conn = get_db()
        conn.execute(
            "DELETE FROM users WHERE email = ? AND deleted_at IS NULL",
            (email,)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "success": False,
            "message": "We could not send the verification email. Please try again."
        }), 500


    return jsonify({
        "success": True,
        "message": "Registration successful. Check your email."
    }), 201
    




    
@auth.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    if not request.is_json:
        return jsonify({
            "success": False,
            "message": "Request must be JSON"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON data"
        }), 400
    

    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Email and password must be text"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password required"
        }), 400

    if len(email) > MAX_EMAIL_LENGTH:
        return jsonify({
            "success": False,
            "message": "Email address is too long"
        }), 400

    if len(password) > MAX_PASSWORD_LENGTH:
        return jsonify({
            "success": False,
            "message": "Password is too long"
        }), 400

        
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? AND deleted_at IS NULL AND is_active = 1",
        (email,)
    ).fetchone()
    conn.close()

    
    if not user:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    # Check if password matches
    password_matches = bcrypt.checkpw(password.encode("utf-8"),user["password_hash"].encode("utf-8")
    )

    if not password_matches:
        return jsonify({"success": False, "message": "Invalid email or password"}), 401
    

    if not user["is_verified"]:
        return jsonify({
            "success": False,
            "message": "Please verify your email before logging in.",
            "needs_verification": True
        }), 403

    # Create JWT token
    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"], "email": user["email"]},
        expires_delta=timedelta(hours=1)
    )

    return jsonify({
        "success": True,
        "message": "Login successful",
        "token": token,
        "role": user["role"]
    }), 200




@auth.route("/verify-otp", methods=["POST"])
@limiter.limit("5 per minute")
def verify_otp():

    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Invalid JSON data"}), 400

    email = data.get("email", "")
    otp   = data.get("otp", "")

    if not isinstance(email, str) or not isinstance(otp, str):
        return jsonify({"success": False, "message": "Email and code must be text"}), 400

    email = email.strip().lower()
    otp   = otp.strip()

    if not email or not otp:
        return jsonify({"success": False, "message": "Email and code are required"}), 400

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND deleted_at IS NULL AND is_active = 1", (email,)).fetchone()

    if not user:
        conn.close()
        return jsonify({"success": False, "message": "Invalid email or code"}), 400

    if user["is_verified"]:
        conn.close()
        return jsonify({"success": True, "message": "Email already verified"}), 200

    if is_otp_expired(user["otp_expires_at"]):
        conn.close()
        return jsonify({"success": False, "message": "Code expired. Request a new one."}), 400

    if hash_otp(otp) != user["otp_hash"]:
        conn.close()
        return jsonify({"success": False, "message": "Incorrect code"}), 400

    conn.execute(
        "UPDATE users SET is_verified = 1, otp_hash = NULL, otp_expires_at = NULL WHERE email = ?AND deleted_at IS NULL",
        (email,)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Email verified! You can now log in."}), 200


@auth.route("/resend-otp", methods=["POST"])
@limiter.limit("5 per minute")
def resend_otp():

    if not request.is_json:
        return jsonify({"success": False, "message": "Request must be JSON"}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Invalid JSON data"}), 400

    email = data.get("email", "")
    if not isinstance(email, str) or not email.strip():
        return jsonify({"success": False, "message": "Email is required"}), 400

    email = email.strip().lower()

    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND deleted_at IS NULL AND is_active = 1", (email,)).fetchone()

    if not user:
        conn.close()
        return jsonify({"success": True, "message": "If that account exists, a new code was sent."}), 200

    if user["is_verified"]:
        conn.close()
        return jsonify({"success": True, "message": "Email already verified"}), 200

    otp = generate_otp()

    otp_hash = hash_otp(otp)
    otp_expires_at = otp_expiry_timestamp()

    conn.execute(
        """UPDATE users
        SET otp_hash = ?, otp_expires_at = ?
        WHERE email = ? AND deleted_at IS NULL""",
        (otp_hash, otp_expires_at, email)
    )

    conn.commit()
    conn.close()


    # Send the new OTP directly from the backend
    email_sent = send_otp_email(email, otp)

    if not email_sent:
        return jsonify({
            "success": False,
            "message": "Could not send the verification email. Please try again."
        }), 500


    return jsonify({
        "success": True,
        "message": "A new verification code has been sent."
    }), 200



    