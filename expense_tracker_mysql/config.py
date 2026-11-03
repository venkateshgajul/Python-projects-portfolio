"""Database settings. Edit these, or set environment variables instead (safer for passwords)."""
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "your_password_here"),
    "port": int(os.getenv("DB_PORT", "3306")),
}
DB_NAME = os.getenv("DB_NAME", "expense_tracker")
