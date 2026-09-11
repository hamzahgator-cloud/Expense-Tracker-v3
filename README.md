# Expense Tracker v3

A full-stack expense tracking web app with user authentication, admin controls, and spending analytics.

This is the third version of my Expense Tracker learning project.

- **v1:** Python CLI + JSON storage  
- **v2:** Python CLI + SQLite database  
- **v3:** Flask API + HTML/CSS/JS frontend (this version)

---

## Features

### Users
- Register with email verification (OTP)
- Secure login with JWT
- Add, update, delete expenses
- Search and filter expenses
- Dashboard totals, averages, min/max
- Charts for category and spending over time

### Admin
- Separate admin dashboard
- View all users
- Activate / deactivate users
- Soft-delete users
- System summary stats

### Security
- Password hashing (bcrypt)
- JWT authentication
- Role-based access (user / admin)
- Email validation
- Soft delete + account deactivation
- Foreign keys between users and expenses



## Tech Stack

**Backend**
- Python
- Flask
- Flask-JWT-Extended
- Flask-CORS
- Flask-Limiter
- SQLite
- bcrypt
- EmailJS (OTP emails)

**Frontend**
- HTML
- CSS
- JavaScript (vanilla)
- Chart.js



## Project Structure

```text
Expense-Tracker-v3/
├── app.py              # Flask routes
├── auth.py             # Auth + OTP + users table
├── repository.py       # Database layer
├── service.py          # Business logic
├── expense.py          # Expense model
├── extensions.py       # Shared extensions
├── make_admin.py       # Helper script to promote admin
├── index.html          # User dashboard
├── admin.html          # Admin dashboard
├── login.html
├── register.html
├── verify.html
├── script.js
├── admin.js
├── auth.js
├── verify.js
├── style.css
├── admin.css
└── .gitignore

