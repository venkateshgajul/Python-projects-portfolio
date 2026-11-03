# Expense Tracker (Python + MySQL)

Add, edit, delete and categorize expenses, view monthly summaries, export to CSV.

## Setup
1. Install MySQL Server and make sure it is running.
2. Install the connector:  `pip install -r requirements.txt`
3. Open `config.py` and put your MySQL password (or set the DB_PASSWORD environment variable).
4. Run:
   - CLI: `python main.py`
   - GUI: `python gui.py`  (Tkinter)

The database `expense_tracker` and the `expenses` table are created automatically on first run.
`schema.sql` shows the same SQL plus sample reporting queries.

## Files
- config.py  - connection settings
- tracker.py - OOP class with all MySQL queries (parameterised, to prevent SQL injection)
- main.py    - command-line menu
- gui.py     - Tkinter interface
- schema.sql - table definition and sample queries
