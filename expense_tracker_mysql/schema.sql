-- Optional: run this manually in MySQL Workbench / terminal.
-- tracker.py also creates these automatically on first run.
CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    expense_date DATE NOT NULL,
    category VARCHAR(30) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Handy queries to show in an interview:
-- Monthly total per category
SELECT category, SUM(amount) AS total
FROM expenses
WHERE YEAR(expense_date) = 2026 AND MONTH(expense_date) = 11
GROUP BY category
ORDER BY total DESC;

-- Spending per month
SELECT DATE_FORMAT(expense_date, '%Y-%m') AS month, SUM(amount) AS total
FROM expenses
GROUP BY month
ORDER BY month;
