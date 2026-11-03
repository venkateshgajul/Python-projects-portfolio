"""Tkinter GUI for the Expense Tracker.  Run: python gui.py"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tracker import ExpenseTracker, CATEGORIES


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("760x520")
        self.tracker = ExpenseTracker()
        self.selected_id = None
        self._build_form()
        self._build_table()
        self.refresh()

    def _build_form(self):
        form = ttk.LabelFrame(self, text="Expense details", padding=10)
        form.pack(fill="x", padx=10, pady=8)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        self.amt_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        fields = [("Date (YYYY-MM-DD)", ttk.Entry(form, textvariable=self.date_var)),
                  ("Category", ttk.Combobox(form, textvariable=self.cat_var, values=CATEGORIES, state="readonly")),
                  ("Amount", ttk.Entry(form, textvariable=self.amt_var)),
                  ("Description", ttk.Entry(form, textvariable=self.desc_var))]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i // 2, column=(i % 2) * 2, sticky="w", padx=5, pady=4)
            widget.grid(row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=4, sticky="ew")
        btns = ttk.Frame(form)
        btns.grid(row=2, column=0, columnspan=4, pady=6)
        for text, cmd in [("Add", self.add), ("Update", self.update), ("Delete", self.delete),
                          ("Clear", self.clear), ("Monthly Summary", self.summary)]:
            ttk.Button(btns, text=text, command=cmd).pack(side="left", padx=4)

    def _build_table(self):
        cols = ("id", "date", "category", "amount", "description")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c, w in zip(cols, (40, 100, 110, 90, 350)):
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.total_label = ttk.Label(self, text="")
        self.total_label.pack(pady=4)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.tracker.list_all()
        for r in rows:
            self.tree.insert("", "end", values=(r["id"], r["date"], r["category"], f"{r['amount']:.2f}", r["description"]))
        self.total_label.config(text=f"Total of all expenses: {sum(r['amount'] for r in rows):.2f}")

    def values(self):
        return (self.date_var.get().strip(), self.cat_var.get(), self.amt_var.get().strip(), self.desc_var.get().strip())

    def add(self):
        try:
            self.tracker.add(*self.values())
            self.clear()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def update(self):
        if self.selected_id is None:
            return messagebox.showinfo("Select", "Select an expense from the table first.")
        try:
            self.tracker.update(self.selected_id, *self.values())
            self.clear()
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete(self):
        if self.selected_id is None:
            return messagebox.showinfo("Select", "Select an expense from the table first.")
        if messagebox.askyesno("Confirm", "Delete this expense?"):
            self.tracker.delete(self.selected_id)
            self.clear()
            self.refresh()

    def clear(self):
        self.selected_id = None
        self.date_var.set(date.today().isoformat())
        self.cat_var.set(CATEGORIES[0])
        self.amt_var.set("")
        self.desc_var.set("")

    def on_select(self, _event):
        sel = self.tree.selection()
        if sel:
            eid, dt, cat, amt, desc = self.tree.item(sel[0])["values"]
            self.selected_id = eid
            self.date_var.set(dt)
            self.cat_var.set(cat)
            self.amt_var.set(amt)
            self.desc_var.set(desc)

    def summary(self):
        month = self.date_var.get().strip()[:7]
        by_cat, total = self.tracker.monthly_summary(month)
        if not by_cat:
            return messagebox.showinfo("Summary", f"No expenses for {month}.")
        lines = [f"{c}: {a:.2f} ({a / total * 100:.1f}%)" for c, a in by_cat.items()]
        messagebox.showinfo(f"Summary for {month}", "\n".join(lines) + f"\n\nTOTAL: {total:.2f}")


if __name__ == "__main__":
    App().mainloop()
