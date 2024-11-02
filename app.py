import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv
import matplotlib.pyplot as plt
import sqlite3
from tkcalendar import Calendar
import bcrypt

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management ERP")
        self.root.geometry("800x600")
        self.root.configure(bg="#ffffff")

        self.inventory = []
        self.current_user = None

        # Initialize database
        self.init_db()
        self.create_login_window()

    def init_db(self):
        self.conn = sqlite3.connect("users.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            org_name TEXT NOT NULL,
            dob TEXT NOT NULL,
            role TEXT NOT NULL,
            gender TEXT NOT NULL,
            password TEXT NOT NULL
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )''')
        self.conn.commit()

    def create_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("300x250")
        self.login_window.configure(bg="#ffffff")

        tk.Label(self.login_window, text="Email", bg="#ffffff").pack(pady=10)
        self.email_entry = tk.Entry(self.login_window)
        self.email_entry.pack(pady=5)

        tk.Label(self.login_window, text="Password", bg="#ffffff").pack(pady=10)
        self.password_entry = tk.Entry(self.login_window, show='*')
        self.password_entry.pack(pady=5)

        tk.Button(self.login_window, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.login_window, text="Sign Up", command=self.create_signup_window).pack(pady=5)

    def create_signup_window(self):
        self.signup_window = tk.Toplevel(self.root)
        self.signup_window.title("Sign Up")
        self.signup_window.geometry("400x450")
        self.signup_window.configure(bg="#ffffff")

        tk.Label(self.signup_window, text="Name", bg="#ffffff").pack(pady=5)
        self.name_entry = tk.Entry(self.signup_window)
        self.name_entry.pack(pady=5)

        tk.Label(self.signup_window, text="Email ID", bg="#ffffff").pack(pady=5)
        self.email_entry_signup = tk.Entry(self.signup_window)
        self.email_entry_signup.pack(pady=5)

        tk.Label(self.signup_window, text="Organization Name", bg="#ffffff").pack(pady=5)
        self.org_entry = tk.Entry(self.signup_window)
        self.org_entry.pack(pady=5)

        tk.Label(self.signup_window, text="Date of Birth", bg="#ffffff").pack(pady=5)
        self.dob_calendar = Calendar(self.signup_window)
        self.dob_calendar.pack(pady=5)

        tk.Label(self.signup_window, text="Role", bg="#ffffff").pack(pady=5)
        self.role_var = tk.StringVar()
        self.role_dropdown = ttk.Combobox(self.signup_window, textvariable=self.role_var, values=["Admin", "Manager", "Employee", "User"])
        self.role_dropdown.pack(pady=5)

        tk.Label(self.signup_window, text="Gender", bg="#ffffff").pack(pady=5)
        self.gender_var = tk.StringVar()
        self.gender_frame = ttk.Frame(self.signup_window)
        self.gender_frame.pack(pady=5)
        ttk.Radiobutton(self.gender_frame, text="Male", variable=self.gender_var, value="Male").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.gender_frame, text="Female", variable=self.gender_var, value="Female").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.gender_frame, text="Other", variable=self.gender_var, value="Other").pack(side=tk.LEFT, padx=10)

        tk.Label(self.signup_window, text="Password", bg="#ffffff").pack(pady=5)
        self.password_entry_signup = tk.Entry(self.signup_window, show='*')
        self.password_entry_signup.pack(pady=5)

        tk.Button(self.signup_window, text="Sign Up", command=self.signup).pack(pady=20)

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        self.cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = self.cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[7].encode('utf-8')):
            self.current_user = user
            messagebox.showinfo("Login", f"Welcome, {user[1]}!")
            self.login_window.destroy()
            self.create_main_interface()
        else:
            messagebox.showerror("Login Error", "Invalid email or password.")

    def signup(self):
        name = self.name_entry.get().strip()
        email = self.email_entry_signup.get().strip()
        org_name = self.org_entry.get().strip()
        dob = self.dob_calendar.get_date()
        role = self.role_var.get()
        gender = self.gender_var.get()
        password = self.password_entry_signup.get().strip()

        if not all([name, email, org_name, dob, role, gender, password]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            self.cursor.execute("INSERT INTO users (name, email, org_name, dob, role, gender, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (name, email, org_name, dob, role, gender, hashed_password.decode('utf-8')))
            self.conn.commit()
            messagebox.showinfo("Sign Up", "Sign up successful!")
            self.signup_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Sign Up Error", "Email already registered.")

    def create_main_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')
        self.create_inventory_tab()
        self.create_profile_tab()
        if self.current_user[5] == "Admin":
            self.create_user_management_tab()

    def create_inventory_tab(self):
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="Inventory Management")

        # Input frame
        input_frame = ttk.LabelFrame(self.inventory_frame, text="Add / Edit Item", padding=(10, 10))
        input_frame.pack(padx=10, pady=10, fill='x')

        tk.Label(input_frame, text="Item ID").grid(row=0, column=0, sticky='w', padx=5)
        tk.Label(input_frame, text="Item Name").grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(input_frame, text="Quantity").grid(row=0, column=2, sticky='w', padx=5)

        self.item_id_entry = tk.Entry(input_frame)
        self.item_id_entry.grid(row=1, column=0, padx=5)

        self.item_name_entry = tk.Entry(input_frame)
        self.item_name_entry.grid(row=1, column=1, padx=5)

        self.quantity_entry = tk.Entry(input_frame)
        self.quantity_entry.grid(row=1, column=2, padx=5)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=1, column=3, padx=5)

        self.add_button = ttk.Button(button_frame, text="Add Item", command=self.add_item)
        self.add_button.grid(row=0, column=0, padx=5)

        self.edit_button = ttk.Button(button_frame, text="Edit Item", command=self.edit_item)
        self.edit_button.grid(row=0, column=1, padx=5)

        self.delete_button = ttk.Button(button_frame, text="Delete Item", command=self.delete_item)
        self.delete_button.grid(row=0, column=2, padx=5)

        # Search entry for filtering inventory
        self.search_entry = tk.Entry(self.inventory_frame)
        self.search_entry.pack(pady=10)
        self.search_entry.insert(0, "Search by item name...")
        self.search_entry.bind('<KeyRelease>', self.filter_inventory)

        # Treeview for inventory display
        self.tree = ttk.Treeview(self.inventory_frame, columns=("Item ID", "Item Name", "Quantity", "Added By"), show='headings', height=15)
        self.tree.heading("Item ID", text="Item ID")
        self.tree.heading("Item Name", text="Item Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Added By", text="Added By")
        self.tree.pack(pady=10, padx=10, fill='both', expand=True)

        # Action buttons
        action_frame = ttk.LabelFrame(self.inventory_frame, text="Actions", padding=(10, 10))
        action_frame.pack(padx=10, pady=10, fill='x')

        self.save_button = ttk.Button(action_frame, text="Save to File", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(action_frame, text="Load from File", command=self.load_from_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.view_chart_button = ttk.Button(action_frame, text="View Pie Chart", command=self.view_pie_chart)
        self.view_chart_button.pack(side=tk.LEFT, padx=5)

        self.load_inventory()

    def load_inventory(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM inventory WHERE user_id=?", (self.current_user[0],))
        items = self.cursor.fetchall()
        for item in items:
            self.tree.insert("", "end", values=(item[0], item[1], item[2], self.current_user[1]))

    def add_item(self):
        item_id = self.item_id_entry.get().strip()
        item_name = self.item_name_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not item_id or not item_name or not quantity.isdigit():
            messagebox.showerror("Input Error", "Please fill in all fields correctly.")
            return

        self.cursor.execute("INSERT INTO inventory (id, name, quantity, user_id) VALUES (?, ?, ?, ?)",
                            (item_id, item_name, int(quantity), self.current_user[0]))
        self.conn.commit()
        self.load_inventory()
        self.item_id_entry.delete(0, tk.END)
        self.item_name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def edit_item(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to edit.")
            return

        item_id = self.tree.item(selected_item)["values"][0]
        item_name = self.item_name_entry.get().strip()
        quantity = self.quantity_entry.get().strip()

        if not item_name or not quantity.isdigit():
            messagebox.showerror("Input Error", "Please fill in all fields correctly.")
            return

        self.cursor.execute("UPDATE inventory SET name=?, quantity=? WHERE id=?",
                            (item_name, int(quantity), item_id))
        self.conn.commit()
        self.load_inventory()

    def delete_item(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return

        item_id = self.tree.item(selected_item)["values"][0]
        self.cursor.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        self.conn.commit()
        self.load_inventory()

    def filter_inventory(self, event):
        search_term = self.search_entry.get().lower()
        self.load_inventory()  # Reload all items first
        for item in self.tree.get_children():
            item_values = self.tree.item(item)["values"]
            if search_term not in item_values[1].lower():
                self.tree.detach(item)  # Remove it from the tree view
            else:
                self.tree.reattach(item, '')  # Show the item again if it matches

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Item ID", "Item Name", "Quantity", "Added By"])
            for item in self.tree.get_children():
                writer.writerow(self.tree.item(item)["values"])

        messagebox.showinfo("Save to File", "Inventory saved successfully!")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                item_id, item_name, quantity, added_by = row
                self.cursor.execute("INSERT INTO inventory (id, name, quantity, user_id) VALUES (?, ?, ?, ?)",
                                    (item_id, item_name, int(quantity), self.current_user[0]))
        self.conn.commit()
        self.load_inventory()
        messagebox.showinfo("Load from File", "Inventory loaded successfully!")

    def view_pie_chart(self):
        self.cursor.execute("SELECT name, quantity FROM inventory WHERE user_id=?", (self.current_user[0],))
        items = self.cursor.fetchall()
        if not items:
            messagebox.showinfo("No Data", "No inventory data available to display.")
            return

        item_names = [item[0] for item in items]
        quantities = [item[1] for item in items]

        plt.figure(figsize=(8, 6))
        plt.pie(quantities, labels=item_names, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title("Inventory Pie Chart")
        plt.show()

    def create_profile_tab(self):
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="Profile")

        tk.Label(self.profile_frame, text=f"Name: {self.current_user[1]}").pack(pady=10)
        tk.Label(self.profile_frame, text=f"Email: {self.current_user[2]}").pack(pady=10)
        tk.Label(self.profile_frame, text=f"Organization: {self.current_user[3]}").pack(pady=10)
        tk.Label(self.profile_frame, text=f"Date of Birth: {self.current_user[4]}").pack(pady=10)
        tk.Label(self.profile_frame, text=f"Role: {self.current_user[5]}").pack(pady=10)
        tk.Label(self.profile_frame, text=f"Gender: {self.current_user[6]}").pack(pady=10)

    def create_user_management_tab(self):
        self.user_management_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_management_frame, text="User Management")

        tk.Label(self.user_management_frame, text="User Management - Admin").pack(pady=10)

        # Treeview for user display
        self.user_tree = ttk.Treeview(self.user_management_frame, columns=("ID", "Name", "Email", "Organization", "Role"), show='headings', height=15)
        self.user_tree.heading("ID", text="ID")
        self.user_tree.heading("Name", text="Name")
        self.user_tree.heading("Email", text="Email")
        self.user_tree.heading("Organization", text="Organization")
        self.user_tree.heading("Role", text="Role")
        self.user_tree.pack(pady=10, padx=10, fill='both', expand=True)

        self.load_users()

        # Buttons for user management
        button_frame = ttk.Frame(self.user_management_frame)
        button_frame.pack(pady=10)

        self.add_user_button = ttk.Button(button_frame, text="Add User", command=self.add_user)
        self.add_user_button.pack(side=tk.LEFT, padx=5)

        self.edit_user_button = ttk.Button(button_frame, text="Edit User", command=self.edit_user)
        self.edit_user_button.pack(side=tk.LEFT, padx=5)

        self.delete_user_button = ttk.Button(button_frame, text="Delete User", command=self.delete_user)
        self.delete_user_button.pack(side=tk.LEFT, padx=5)

    def load_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        self.cursor.execute("SELECT id, name, email, org_name, role FROM users")
        users = self.cursor.fetchall()
        for user in users:
            self.user_tree.insert("", "end", values=user)

    def add_user(self):
        # Logic to add a new user
        self.new_user_window = tk.Toplevel(self.root)
        self.new_user_window.title("Add User")
        self.new_user_window.geometry("400x450")

        tk.Label(self.new_user_window, text="Name").pack(pady=5)
        name_entry = tk.Entry(self.new_user_window)
        name_entry.pack(pady=5)

        tk.Label(self.new_user_window, text="Email").pack(pady=5)
        email_entry = tk.Entry(self.new_user_window)
        email_entry.pack(pady=5)

        tk.Label(self.new_user_window, text="Organization Name").pack(pady=5)
        org_entry = tk.Entry(self.new_user_window)
        org_entry.pack(pady=5)

        tk.Label(self.new_user_window, text="Date of Birth").pack(pady=5)
        dob_calendar = Calendar(self.new_user_window)
        dob_calendar.pack(pady=5)

        tk.Label(self.new_user_window, text="Role").pack(pady=5)
        role_var = tk.StringVar()
        role_dropdown = ttk.Combobox(self.new_user_window, textvariable=role_var, values=["Admin", "Manager", "Employee", "User"])
        role_dropdown.pack(pady=5)

        tk.Label(self.new_user_window, text="Gender").pack(pady=5)
        gender_var = tk.StringVar()
        gender_frame = ttk.Frame(self.new_user_window)
        gender_frame.pack(pady=5)
        ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other").pack(side=tk.LEFT, padx=10)

        tk.Label(self.new_user_window, text="Password").pack(pady=5)
        password_entry = tk.Entry(self.new_user_window, show='*')
        password_entry.pack(pady=5)

        tk.Button(self.new_user_window, text="Add User", command=lambda: self.save_new_user(name_entry, email_entry, org_entry, dob_calendar, role_var, gender_var, password_entry)).pack(pady=20)

    def save_new_user(self, name_entry, email_entry, org_entry, dob_calendar, role_var, gender_var, password_entry):
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        org_name = org_entry.get().strip()
        dob = dob_calendar.get_date()
        role = role_var.get()
        gender = gender_var.get()
        password = password_entry.get().strip()

        if not all([name, email, org_name, dob, role, gender, password]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            self.cursor.execute("INSERT INTO users (name, email, org_name, dob, role, gender, password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (name, email, org_name, dob, role, gender, hashed_password.decode('utf-8')))
            self.conn.commit()
            messagebox.showinfo("Add User", "User added successfully!")
            self.new_user_window.destroy()
            self.load_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Add User Error", "Email already registered.")

    def edit_user(self):
        selected_item = self.user_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a user to edit.")
            return

        user_id = self.user_tree.item(selected_item)["values"][0]
        self.edit_user_window = tk.Toplevel(self.root)
        self.edit_user_window.title("Edit User")
        self.edit_user_window.geometry("400x450")

        # Load user data for editing
        self.cursor.execute("SELECT name, email, org_name, dob, role, gender FROM users WHERE id=?", (user_id,))
        user = self.cursor.fetchone()

        tk.Label(self.edit_user_window, text="Name").pack(pady=5)
        name_entry = tk.Entry(self.edit_user_window)
        name_entry.insert(0, user[0])
        name_entry.pack(pady=5)

        tk.Label(self.edit_user_window, text="Email").pack(pady=5)
        email_entry = tk.Entry(self.edit_user_window)
        email_entry.insert(0, user[1])
        email_entry.pack(pady=5)

        tk.Label(self.edit_user_window, text="Organization Name").pack(pady=5)
        org_entry = tk.Entry(self.edit_user_window)
        org_entry.insert(0, user[2])
        org_entry.pack(pady=5)

        tk.Label(self.edit_user_window, text="Date of Birth").pack(pady=5)
        dob_calendar = Calendar(self.edit_user_window)
        dob_calendar.set_date(user[3])
        dob_calendar.pack(pady=5)

        tk.Label(self.edit_user_window, text="Role").pack(pady=5)
        role_var = tk.StringVar(value=user[4])
        role_dropdown = ttk.Combobox(self.edit_user_window, textvariable=role_var, values=["Admin", "Manager", "Employee", "User"])
        role_dropdown.pack(pady=5)

        tk.Label(self.edit_user_window, text="Gender").pack(pady=5)
        gender_var = tk.StringVar(value=user[5])
        gender_frame = ttk.Frame(self.edit_user_window)
        gender_frame.pack(pady=5)
        ttk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other").pack(side=tk.LEFT, padx=10)

        tk.Button(self.edit_user_window, text="Save Changes", command=lambda: self.save_user_changes(user_id, name_entry, email_entry, org_entry, dob_calendar, role_var, gender_var)).pack(pady=20)

    def save_user_changes(self, user_id, name_entry, email_entry, org_entry, dob_calendar, role_var, gender_var):
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        org_name = org_entry.get().strip()
        dob = dob_calendar.get_date()
        role = role_var.get()
        gender = gender_var.get()

        if not all([name, email, org_name, dob, role, gender]):
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        self.cursor.execute("UPDATE users SET name=?, email=?, org_name=?, dob=?, role=?, gender=? WHERE id=?",
                            (name, email, org_name, dob, role, gender, user_id))
        self.conn.commit()
        messagebox.showinfo("Edit User", "User updated successfully!")
        self.edit_user_window.destroy()
        self.load_users()

    def delete_user(self):
        selected_item = self.user_tree.focus()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a user to delete.")
            return

        user_id = self.user_tree.item(selected_item)["values"][0]
        self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        self.conn.commit()
        messagebox.showinfo("Delete User", "User deleted successfully!")
        self.load_users()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
