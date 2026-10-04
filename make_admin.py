import os
import sqlite3
import sys


# simple way but not recommended

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "expense.db")

def make_admin():
    email = "...@gmail.com"   
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "UPDATE users SET role = 'admin' WHERE email = ? AND deleted_at IS NULL",
        (email,)
    )
    conn.commit()
    print("Updated rows:", cursor.rowcount)
    conn.close()

def remove_admin():
    email = "quraninenglish123@gmail.com"   
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "UPDATE users SET role = 'user' WHERE email = ? AND deleted_at IS NULL",
        (email,)
    )
    conn.commit()
    print("Updated rows:", cursor.rowcount)
    conn.close()

# Run only one at a time:
# make_admin()
remove_admin()



# complex at fiirst but best


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "expense.db")


# def set_role(email, role):
#     email = email.strip().lower()

#     if not email:
#         print("Please provide an email.")
#         return

#     if role not in ("admin", "user"):
#         print("Role must be admin or user.")
#         return

#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.execute(
#         """
#         UPDATE users
#         SET role = ?
#         WHERE email = ?
#           AND deleted_at IS NULL
#         """,
#         (role, email)
#     )
#     conn.commit()
#     updated = cursor.rowcount
#     conn.close()

#     if updated == 0:
#         print(f"No active user found with email: {email}")
#     else:
#         print(f"Role updated to '{role}' for: {email}")


# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Usage:")
#         print("  python make_admin.py make your@email.com")
#         print("  python make_admin.py remove your@email.com")
#     else:
#         action = sys.argv[1].strip().lower()
#         email = sys.argv[2]

#         if action == "make":
#             set_role(email, "admin")
#         elif action == "remove":
#             set_role(email, "user")
#         else:
#             print("Action must be 'make' or 'remove'")