import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

# ---------------- DATABASE SETUP ---------------- #
conn = sqlite3.connect('pharmacy.db')
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    qty INTEGER NOT NULL,
    price REAL NOT NULL
)
""")
conn.commit()

# ---------------- APP WINDOW ---------------- #
root = tk.Tk()
root.title("💊 Pharmacy Management System")
root.geometry("900x550")
root.configure(bg="#f8f9fa")

# Modern Styling
style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview",
                background="#ffffff",
                foreground="black",
                rowheight=25,
                fieldbackground="#ffffff")
style.map('Treeview', background=[('selected', '#4caf50')])

style.configure("TButton",
                font=('Segoe UI', 10, 'bold'),
                background="#4caf50",
                foreground="white",
                borderwidth=0,
                focusthickness=3,
                focuscolor='none',
                padding=6)
style.map("TButton", background=[('active', '#43a047')])

# ---------------- FUNCTIONS ---------------- #
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    cur.execute("SELECT * FROM medicines")
    rows = cur.fetchall()
    for r in rows:
        tree.insert("", "end", values=r)
    update_total_value()

def add_medicine():
    name = name_entry.get().strip()
    qty = qty_entry.get().strip()
    price = price_entry.get().strip()

    if not name or not qty or not price:
        messagebox.showwarning("Warning", "All fields are required!")
        return
    try:
        qty, price = int(qty), float(price)
    except ValueError:
        messagebox.showerror("Error", "Quantity must be integer and Price must be numeric.")
        return

    cur.execute("INSERT INTO medicines (name, qty, price) VALUES (?, ?, ?)", (name, qty, price))
    conn.commit()
    refresh_table()
    name_entry.delete(0, tk.END)
    qty_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to delete.")
        return
    for s in selected:
        item = tree.item(s)
        cur.execute("DELETE FROM medicines WHERE id=?", (item['values'][0],))
    conn.commit()
    refresh_table()

def search_medicine():
    query = search_entry.get().strip()
    for row in tree.get_children():
        tree.delete(row)
    cur.execute("SELECT * FROM medicines WHERE name LIKE ?", ('%' + query + '%',))
    rows = cur.fetchall()
    for r in rows:
        tree.insert("", "end", values=r)
    update_total_value()

def export_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        cur.execute("SELECT * FROM medicines")
        rows = cur.fetchall()
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Quantity", "Price"])
            writer.writerows(rows)
        messagebox.showinfo("Success", "Data exported successfully!")

def update_total_value():
    cur.execute("SELECT SUM(qty * price) FROM medicines")
    total = cur.fetchone()[0]
    total_label.config(text=f"💰 Total Stock Value: ₹{total if total else 0:.2f}")

def on_double_click(event):
    selected = tree.selection()
    if not selected:
        return
    item = tree.item(selected[0])
    edit_window(item['values'])

def edit_window(values):
    edit = tk.Toplevel(root)
    edit.title("Edit Medicine")
    edit.geometry("300x250")
    edit.configure(bg="#f0f0f0")

    tk.Label(edit, text="Medicine Name:", bg="#f0f0f0").pack(pady=5)
    name_edit = tk.Entry(edit)
    name_edit.pack(pady=5)
    name_edit.insert(0, values[1])

    tk.Label(edit, text="Quantity:", bg="#f0f0f0").pack(pady=5)
    qty_edit = tk.Entry(edit)
    qty_edit.pack(pady=5)
    qty_edit.insert(0, values[2])

    tk.Label(edit, text="Price:", bg="#f0f0f0").pack(pady=5)
    price_edit = tk.Entry(edit)
    price_edit.pack(pady=5)
    price_edit.insert(0, values[3])

    def save_changes():
        new_name = name_edit.get().strip()
        new_qty = qty_edit.get().strip()
        new_price = price_edit.get().strip()
        try:
            new_qty, new_price = int(new_qty), float(new_price)
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity or price.")
            return
        cur.execute("UPDATE medicines SET name=?, qty=?, price=? WHERE id=?",
                    (new_name, new_qty, new_price, values[0]))
        conn.commit()
        refresh_table()
        edit.destroy()

    ttk.Button(edit, text="Save", command=save_changes).pack(pady=15)

# ---------------- UI DESIGN ---------------- #
frame_top = tk.Frame(root, bg="#f8f9fa")
frame_top.pack(pady=10)

tk.Label(frame_top, text="Medicine Name:", bg="#f8f9fa").grid(row=0, column=0, padx=5)
name_entry = ttk.Entry(frame_top, width=20)
name_entry.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Quantity:", bg="#f8f9fa").grid(row=0, column=2, padx=5)
qty_entry = ttk.Entry(frame_top, width=10)
qty_entry.grid(row=0, column=3, padx=5)

tk.Label(frame_top, text="Price:", bg="#f8f9fa").grid(row=0, column=4, padx=5)
price_entry = ttk.Entry(frame_top, width=10)
price_entry.grid(row=0, column=5, padx=5)

ttk.Button(frame_top, text="Add", command=add_medicine).grid(row=0, column=6, padx=5)
ttk.Button(frame_top, text="Delete", command=delete_selected).grid(row=0, column=7, padx=5)

# Search bar
frame_search = tk.Frame(root, bg="#f8f9fa")
frame_search.pack(pady=10)
tk.Label(frame_search, text="🔍 Search:", bg="#f8f9fa").pack(side=tk.LEFT, padx=5)
search_entry = ttk.Entry(frame_search, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(frame_search, text="Search", command=search_medicine).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_search, text="Show All", command=refresh_table).pack(side=tk.LEFT, padx=5)
ttk.Button(frame_search, text="Export CSV", command=export_csv).pack(side=tk.LEFT, padx=5)

# Table
tree = ttk.Treeview(root, columns=("ID", "Name", "Quantity", "Price"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Quantity", text="Quantity")
tree.heading("Price", text="Price (₹)")
tree.pack(fill="both", expand=True, padx=20, pady=10)

tree.bind("<Double-1>", on_double_click)

# Bottom total label
total_label = tk.Label(root, text="💰 Total Stock Value: ₹0.00", bg="#f8f9fa", font=("Segoe UI", 11, "bold"))
total_label.pack(pady=10)

refresh_table()
root.mainloop()
