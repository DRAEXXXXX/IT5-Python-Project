import tkinter as tk
from tkinter import ttk
from user_management import UserManagementFrame
from product_management import ProductManagementFrame
from sales_report import show_sales_report
from financial_report import show_financial_report
from supplier_management import SupplierManagementFrame

class AdminPanel(tk.Frame):
    def __init__(self, master, switch_frame_callback):
        super().__init__(master)
        self.switch_frame_callback = switch_frame_callback

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, padding=10)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_rowconfigure(6, weight=1)

        ttk.Label(sidebar, text="Admin Menu", font=("Arial", 14)).pack(pady=(0, 20))
        ttk.Button(sidebar, text="Product/Price Management", command=lambda: self.show_section("Product/Price Management")).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Show/Add/Edit/Remove Users", command=lambda: self.show_section("User Management")).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Supplier Management", command=lambda: self.show_section("Supplier Management")).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="View Sales Report", command=lambda: self.show_section("Sales Report")).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="View Financial Report", command=lambda: self.show_section("Financial Report")).pack(fill="x", pady=5)
        ttk.Button(sidebar, text="Logout", command=lambda: self.switch_frame_callback("login")).pack(fill="x", pady=(20, 0))

        self.content = ttk.Frame(self, padding=20)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.current_section = None

        self.section_label = ttk.Label(self.content, text="Welcome to Admin Panel", font=("Arial", 16))
        self.section_label.pack(pady=20)

    def show_section(self, section_name):
        for widget in self.content.winfo_children():
            widget.destroy()

        if section_name == "User Management":
            self.current_section = UserManagementFrame(self.content)
            self.current_section.pack(fill='both', expand=True)

        elif section_name == "Product/Price Management":
            self.current_section = ProductManagementFrame(self.content)
            self.current_section.pack(fill='both', expand=True)

        elif section_name == "Sales Report":
            show_sales_report(self.content)

        elif section_name == "Financial Report":
            show_financial_report(self.content)
        
        elif section_name == "Supplier Management":
            self.current_section = SupplierManagementFrame(self.content)
            self.current_section.pack(fill='both', expand=True)

        else:
            self.section_label = ttk.Label(self.content, text=f"{section_name}", font=("Arial", 16))
            self.section_label.pack(pady=20)
