import tkinter as tk
from tkinter import ttk, messagebox
from db import get_db_connection

class LoginWindow(tk.Frame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.switch_frame = switch_frame_callback

        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        label_font = ("Segoe UI", 12)
        entry_font = ("Segoe UI", 12)
        button_font = ("Segoe UI", 12, "bold")

        ttk.Label(container, text="Username", font=label_font).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.entry_username = ttk.Entry(container, font=entry_font, width=25)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(container, text="Password", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.entry_password = ttk.Entry(container, show="*", font=entry_font, width=25)
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        login_button = ttk.Button(container, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, pady=20)
        login_button.configure(style="Login.TButton")

        style = ttk.Style()
        style.configure("Login.TButton", font=button_font, padding=6)

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        user = self.validate_login(username, password)
        if user:
            role = user['role'].lower()
            user_id = user['user_id']
            if role == 'admin':
                self.switch_frame("admin")
            else:
                self.switch_frame("cashier", user_id=user_id)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def validate_login(self, username, password):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and user['password_hash'] == password:
                return user
            return None
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return None
