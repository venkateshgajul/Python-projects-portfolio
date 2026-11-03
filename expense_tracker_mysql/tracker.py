"""Core logic for the Expense Tracker (OOP + MySQL)."""
import csv
from datetime import datetime

import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG, DB_NAME

CATEGORIES = ["Food", "Travel", "Rent", "Shopping", "Bills", "Health", "Entertainment", "Other"]


class ExpenseTracker:
    def __init__(self):
        try:
            # Connect to the server, create the database if needed, then select it
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
            self.conn.database = DB_NAME
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS expenses (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       expense_date DATE NOT NULL,
                       category VARCHAR(30) NOT NULL,
                       amount DECIMAL(10,2) NOT NULL,
                       description VARCHAR(255) DEFAULT '',
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )"""
            )
            self.conn.commit()
        except Error as e:
            raise ConnectionError(
                f"Could not connect to MySQL: {e}\n"
                "Check that MySQL is running and the details in config.py are correct."
            )

    # ---------- validation ----------
    @staticmethod
    def _validate(date, category, amount):
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")
        if category not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than 0.")
        return amount

    @staticmethod
    def _clean(row):
        """Convert MySQL types (date, Decimal) into plain Python types."""
        return {
            "id": row["id"],
            "date": row["expense_date"].isoformat(),
            "category": row["category"],
            "amount": float(row["amount"]),
            "description": row["description"] or "",
        }

    # ---------- CRUD ----------
    def add(self, date, category, amount, description=""):
        amount = self._validate(date, category, amount)
        self.cursor.execute(
            "INSERT INTO expenses (expense_date, category, amount, description) VALUES (%s, %s, %s, %s)",
            (date, category, amount, description),
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, expense_id, date, category, amount, description=""):
        amount = self._validate(date, category, amount)
        self.cursor.execute(
            "UPDATE expenses SET expense_date=%s, category=%s, amount=%s, description=%s WHERE id=%s",
            (date, category, amount, description, expense_id),
        )
        self.conn.commit()
        if not self._exists(expense_id):
            raise ValueError(f"No expense found with id {expense_id}.")

    def delete(self, expense_id):
        if not self._exists(expense_id):
            raise ValueError(f"No expense found with id {expense_id}.")
        self.cursor.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
        self.conn.commit()

    def _exists(self, expense_id):
        self.cursor.execute("SELECT 1 AS found FROM expenses WHERE id=%s", (expense_id,))
        return self.cursor.fetchone() is not None

    def list_all(self, month=None):
        """month format: YYYY-MM (optional filter)."""
        if month:
            self.cursor.execute(
                "SELECT * FROM expenses WHERE DATE_FORMAT(expense_date, '%Y-%m') = %s "
                "ORDER BY expense_date DESC, id DESC",
                (month,),
            )
        else:
            self.cursor.execute("SELECT * FROM expenses ORDER BY expense_date DESC, id DESC")
        return [self._clean(r) for r in self.cursor.fetchall()]

    # ---------- reports ----------
    def monthly_summary(self, month):
        """Return ({category: total}, grand_total) for a YYYY-MM month."""
        self.cursor.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE DATE_FORMAT(expense_date, '%Y-%m') = %s "
            "GROUP BY category ORDER BY total DESC",
            (month,),
        )
        by_cat = {r["category"]: float(r["total"]) for r in self.cursor.fetchall()}
        return by_cat, sum(by_cat.values())

    def export_csv(self, path="expenses_export.csv"):
        rows = self.list_all()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "description"])
            writer.writeheader()
            writer.writerows(rows)
        return len(rows)

    def close(self):
        self.cursor.close()
        self.conn.close()
