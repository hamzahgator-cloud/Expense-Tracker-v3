import os
import sqlite3
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "expense.db")

class ExpenseRepository:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = db_path
        self.create_table()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_table(self):
        conn = self.get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER  PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
        conn.close()

    def save_expense_to_db(self, expense):
        conn = self.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO expenses (name, amount, category, date, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (expense.name, expense.amount,
             expense.category, expense.date, expense.user_id)
        )
        conn.commit()
        expense.id = cursor.lastrowid
        conn.close()
        return expense

    def get_expenses_by_user(self, user_id):
        conn = self.get_connection()

        try:
            rows = conn.execute(
                """
                SELECT * FROM expenses
                WHERE user_id = ?
                ORDER BY amount DESC
                """,
                (user_id,)
            ).fetchall()

            return rows

        finally:
            conn.close()


    def search_by_name(self, name, user_id):
        conn = self.get_connection()
        try:

            rows = conn.execute(
                "SELECT * FROM expenses WHERE name LIKE ? AND user_id = ?",
                (f"%{name}%", user_id)
            ).fetchall()
            return rows
        finally:
            conn.close()
            

    def get_expense_by_id(self,expense_id,user_id):
        conn = self.get_connection()
        try:

            rows = conn.execute(
                        "SELECT * FROM expenses WHERE id = ? AND user_id = ?",
                        (expense_id,user_id)
            ).fetchone()
            return rows
        finally:
            conn.close()
        

    def update_expense(self,expense_id, name, amount, category, user_id):
        conn = self.get_connection()
        try:

            conn.execute(
                """
                UPDATE expenses 
                SET name = ?, amount = ?, category = ?
                WHERE user_id = ? AND id = ?
                """,
                (name, amount, category, user_id, expense_id)
            )
            conn.commit()
        finally:
            conn.close()

    def delete_expense_by_id(self, expense_id, user_id):
        conn = self.get_connection()
        try:

            conn.execute(
                "DELETE FROM expenses WHERE id = ? AND user_id = ?",
                (expense_id, user_id)
            )
            conn.commit()
        finally:
            conn.close()

    def get_expenses_by_category(self, category, user_id):
        conn = self.get_connection()
        try:

            rows = conn.execute(
                """
                SELECT * FROM expenses 
                WHERE LOWER(category) LIKE LOWER(?) 
                AND user_id = ? 
                ORDER BY amount DESC
                """,
                (f"%{category}%", user_id)
            ).fetchall()
            return rows
        finally:
            conn.close()
        

    def get_total_expenses(self, user_id):
        conn = self.get_connection()
        try:

            result = conn.execute(
                "SELECT SUM(amount) FROM expenses WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]
            
            return result
        
        finally:
            conn.close()


    def get_expense_count(self, user_id):
        conn = self.get_connection()
        try:

            result = conn.execute(
                "SELECT COUNT(id) FROM expenses WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]
            return result
        finally:
            conn.close()
        

    def get_average_amount(self, user_id):
        conn = self.get_connection()
        try:

            result = conn.execute(
                "SELECT AVG(amount) FROM expenses WHERE user_id = ?",
                (user_id,)
            ).fetchone()[0]
            return result
        finally:
            conn.close()
       

    def get_amount_by_category(self, user_id):
        conn = self.get_connection()
        try:

            rows = conn.execute(
                """
                SELECT category, SUM(amount) AS total 
                FROM expenses 
                WHERE user_id = ?
                GROUP BY category 
                ORDER BY total DESC
                """,
                (user_id,)
            ).fetchall()
            return rows
        finally:
            conn.close()
        

    def get_min_max(self, user_id):
        conn = self.get_connection()
        try:

            rows = conn.execute(
                """
                SELECT name, amount FROM (
                    SELECT name, amount FROM expenses 
                    WHERE user_id = ?
                    ORDER BY amount DESC LIMIT 1
                )
                UNION ALL
                SELECT name, amount FROM (
                    SELECT name, amount FROM expenses 
                    WHERE user_id = ?
                    ORDER BY amount ASC LIMIT 1
                )
                """,
                (user_id, user_id)
            ).fetchall()
            return rows
        finally:
            conn.close()
        





        #For admin only 
    def get_total_users(self):
        conn = self.get_connection()
        try:

            result = conn.execute(
                "SELECT COUNT(*) FROM users WHERE deleted_at IS NULL AND is_active = 1"
            ).fetchone()[0]
            return result
        finally:
            conn.close()
        


    def admin_summary(self):
        conn = self.get_connection()
        try:

            result = conn.execute(
                "SELECT COUNT(id),SUM(amount),AVG(amount) FROM expenses"
            ).fetchone()
            return result
        finally:
            conn.close()
        

    def delete_user(self, user_id):
        conn = self.get_connection()

        try:
            deleted_at = datetime.now(timezone.utc).isoformat()
            cursor = conn.execute(
                """
                UPDATE users
                SET deleted_at = ?
                WHERE id = ? AND deleted_at IS NULL
                """,
                (deleted_at, user_id)
            )
            conn.commit()
            return cursor.rowcount  
        finally:
            conn.close()
            


    def get_all_users(self):

        conn = self.get_connection()
        try:
            rows = conn.execute(
                """
                SELECT id, email, role, is_verified, created_at,is_active
                FROM users
                WHERE deleted_at IS NULL
                ORDER BY id ASC
                """
            ).fetchall()
            return rows
        finally:
            conn.close()

    def deactivate_user(self, user_id):
        conn = self.get_connection()
        try:
            row = conn.execute(
                "UPDATE users SET is_active = 0 WHERE id = ? AND deleted_at IS NULL AND is_active = 1",(user_id,)
            )
            conn.commit()
            return row.rowcount  
        finally:
                conn.close()

    def activate_user(self, user_id):
            conn = self.get_connection()
            try:
                row = conn.execute(
                    "UPDATE users SET is_active = 1 WHERE id = ? AND deleted_at IS NULL AND is_active = 0",(user_id,)
                )
                conn.commit()
                return row.rowcount  
            finally:
                    conn.close()


   

