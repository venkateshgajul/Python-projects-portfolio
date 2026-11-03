"""Command-line interface for the Expense Tracker.  Run: python main.py"""
from datetime import date
from tracker import ExpenseTracker, CATEGORIES

MENU = """
===== EXPENSE TRACKER =====
1. Add expense
2. View expenses
3. Edit expense
4. Delete expense
5. Monthly summary
6. Export to CSV
0. Exit
"""


def ask_details(defaults=None):
    d = defaults or {}
    today = d.get("date", date.today().isoformat())
    dt = input(f"Date [{today}]: ").strip() or today
    print("Categories:", ", ".join(CATEGORIES))
    cat = input(f"Category [{d.get('category', 'Food')}]: ").strip().title() or d.get("category", "Food")
    amt = input(f"Amount [{d.get('amount', '')}]: ").strip() or d.get("amount", "")
    desc = input(f"Description [{d.get('description', '')}]: ").strip() or d.get("description", "")
    return dt, cat, amt, desc


def show(rows):
    if not rows:
        print("No expenses found.")
        return
    print(f"{'ID':<4}{'Date':<12}{'Category':<15}{'Amount':>10}  Description")
    print("-" * 60)
    for r in rows:
        print(f"{r['id']:<4}{r['date']:<12}{r['category']:<15}{r['amount']:>10.2f}  {r['description']}")


def main():
    try:
        tracker = ExpenseTracker()
    except ConnectionError as e:
        print(e)
        return
    while True:
        print(MENU)
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                new_id = tracker.add(*ask_details())
                print(f"Added expense #{new_id}.")
            elif choice == "2":
                month = input("Month (YYYY-MM) or Enter for all: ").strip()
                show(tracker.list_all(month or None))
            elif choice == "3":
                eid = int(input("Expense ID to edit: "))
                current = next((r for r in tracker.list_all() if r["id"] == eid), None)
                if not current:
                    print("ID not found.")
                    continue
                tracker.update(eid, *ask_details(current))
                print("Updated.")
            elif choice == "4":
                tracker.delete(int(input("Expense ID to delete: ")))
                print("Deleted.")
            elif choice == "5":
                month = input("Month (YYYY-MM): ").strip()
                by_cat, total = tracker.monthly_summary(month)
                if not by_cat:
                    print("No data for that month.")
                    continue
                print(f"\nSummary for {month}")
                for cat, amt in by_cat.items():
                    print(f"  {cat:<15}{amt:>10.2f}  ({amt / total * 100:.1f}%)")
                print(f"  {'TOTAL':<15}{total:>10.2f}")
            elif choice == "6":
                print(f"Exported {tracker.export_csv()} rows to expenses_export.csv")
            elif choice == "0":
                tracker.close()
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")
        except ValueError as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
