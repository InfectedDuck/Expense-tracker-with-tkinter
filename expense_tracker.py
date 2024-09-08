import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import sqlite3
import csv
import matplotlib.pyplot as plt

# Connect to SQLite database
conn = sqlite3.connect('expenses.db')
c = conn.cursor()

# Create expenses table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY, item TEXT, amount REAL, date DATE)''')
conn.commit()

budget = 0

# Function to add expense
def add_expense():
    item = item_entry.get()
    amount = amount_entry.get()
    if item and amount:
        try:
            amount = float(amount)
            # Insert expense into database
            c.execute("INSERT INTO expenses (item, amount, date) VALUES (?, ?, DATE('now'))", (item, amount))
            conn.commit()
            messagebox.showinfo("Success", "Expense added successfully!")
            item_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            update_expense_list()
            update_budget_status()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")
    else:
        messagebox.showerror("Error", "Please fill in all fields.")

# Function to delete expense
def delete_expense():
    try:
        selected_index = expense_list.curselection()[0]
        selected_expense = expense_list.get(selected_index)
        expense_id = int(selected_expense.split('.')[0])
        c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()
        update_expense_list()
        update_budget_status()
        messagebox.showinfo("Success", "Expense deleted successfully!")
    except IndexError:
        messagebox.showerror("Error", "Please select an expense to delete.")

# Function to edit expense
def edit_expense():
    try:
        selected_index = expense_list.curselection()[0]
        selected_expense = expense_list.get(selected_index)
        expense_id = int(selected_expense.split('.')[0])
        new_amount = simpledialog.askfloat("Edit Expense", "Enter new amount:")
        if new_amount is not None:
            c.execute("UPDATE expenses SET amount=? WHERE id=?", (new_amount, expense_id))
            conn.commit()
            update_expense_list()
            update_budget_status()
            messagebox.showinfo("Success", "Expense updated successfully!")
    except IndexError:
        messagebox.showerror("Error", "Please select an expense to edit.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")

# Function to filter expenses by date
def filter_expenses():
    selected_date = date_var.get()
    if selected_date:
        c.execute("SELECT * FROM expenses WHERE date=?", (selected_date,))
        filtered_expenses = c.fetchall()
        if filtered_expenses:
            expense_list.delete(0, tk.END)
            for row in filtered_expenses:
                expense_list.insert(tk.END, f"{row[0]}. {row[1]} - ${row[2]} ({row[3]})")
        else:
            messagebox.showinfo("Info", "No expenses found for selected date.")
    else:
        messagebox.showerror("Error", "Please select a date.")

# Function to export expenses to CSV
def export_expenses():
    filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if filename:
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Item', 'Amount', 'Date'])
            c.execute("SELECT * FROM expenses")
            expenses = c.fetchall()
            csvwriter.writerows(expenses)
        messagebox.showinfo("Success", "Expenses exported successfully!")

# Function to update expense list
def update_expense_list():
    expense_list.delete(0, tk.END)
    for row in c.execute("SELECT * FROM expenses"):
        expense_list.insert(tk.END, f"{row[0]}. {row[1]} - ${row[2]} ({row[3]})")

# Function to update budget status
def update_budget_status():
    global budget
    budget_text = budget_entry.get()
    if budget_text:
        try:
            budget = float(budget_text)
            total_expenses = sum(row[2] for row in c.execute("SELECT * FROM expenses"))
            remaining_budget = budget - total_expenses
            if remaining_budget >= 0:
                status_label.config(text=f"Remaining Budget: ${remaining_budget:.2f}", fg="green")
            else:
                status_label.config(text=f"Over Budget by ${abs(remaining_budget):.2f}!", fg="red")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget!")
    else:
        messagebox.showerror("Error", "Please enter a budget!")

# Function to visualize spending
def visualize_spending():
    global budget
    c.execute("SELECT item, amount FROM expenses")
    expenses = c.fetchall()

    category_totals = {}
    total_amount = 0

    for item, amount in expenses:
        total_amount += amount
        category_totals[item] = category_totals.get(item, 0) + amount

    percentages = [(category, (amount / total_amount) * 100) for category, amount in category_totals.items()]

    remaining_budget = budget - total_amount
    if remaining_budget > 0:
        percentages.append(("Remaining Budget", (remaining_budget / budget) * 100))

    labels = [category for category, _ in percentages]
    sizes = [percentage for _, percentage in percentages]

    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Expense Categories Breakdown')
    plt.show()

# GUI setup
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("500x600")
root.configure(bg="#f5f5f5")

style = ttk.Style()
style.configure("TLabel", background="#f5f5f5", font=("Arial", 12))
style.configure("TButton", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))

# Expense entry frame
expense_frame = ttk.Frame(root, padding="10 10 10 10")
expense_frame.pack(pady=10)

ttk.Label(expense_frame, text="Item:").grid(row=0, column=0, padx=5, pady=5)
item_entry = ttk.Entry(expense_frame, width=20)
item_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(expense_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(expense_frame, width=20)
amount_entry.grid(row=1, column=1, padx=5, pady=5)

add_button = ttk.Button(expense_frame, text="Add Expense", command=add_expense)
add_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

edit_button = ttk.Button(expense_frame, text="Edit Expense", command=edit_expense)
edit_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

delete_button = ttk.Button(expense_frame, text="Delete Expense", command=delete_expense)
delete_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Expense list frame
expense_list_frame = ttk.Frame(root, padding="10 10 10 10")
expense_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

ttk.Label(expense_list_frame, text="Expense List", font=("Arial", 14, "bold")).pack(pady=5)
expense_list = tk.Listbox(expense_list_frame, width=50, height=10, font=("Arial", 12))
expense_list.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

# Filter frame
filter_frame = ttk.Frame(root, padding="10 10 10 10")
filter_frame.pack(pady=10)

ttk.Label(filter_frame, text="Filter by Date:").grid(row=0, column=0, padx=5, pady=5)
date_var = tk.StringVar()
date_entry = ttk.Entry(filter_frame, textvariable=date_var)
date_entry.grid(row=0, column=1, padx=5, pady=5)

filter_button = ttk.Button(filter_frame, text="Filter", command=filter_expenses)
filter_button.grid(row=0, column=2, padx=5, pady=5)

# Export frame
export_frame = ttk.Frame(root, padding="10 10 10 10")
export_frame.pack(pady=10)
export_button = ttk.Button(export_frame, text="Export Expenses", command=export_expenses)
export_button.pack(pady=5)

# Budget frame
budget_frame = ttk.Frame(root, padding="10 10 10 10")
budget_frame.pack(pady=10)
ttk.Label(budget_frame, text="Set Budget:").grid(row=0, column=0, padx=5, pady=5)
budget_entry = ttk.Entry(budget_frame)
budget_entry.grid(row=0, column=1, padx=5, pady=5)
status_label = ttk.Label(budget_frame, text="", foreground="green", font=("Arial", 12))
status_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# Visualization frame
visualize_frame = ttk.Frame(root, padding="10 10 10 10")
visualize_frame.pack(pady=10)
visualize_button = ttk.Button(visualize_frame, text="Visualize Spending", command=visualize_spending)
visualize_button.pack(pady=5)

# Update expense list and budget status
update_expense_list()
update_budget_status()

# Start GUI main loop
root.mainloop()

# Close database connection
conn.close()
