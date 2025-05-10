import tkinter as tk
from tkinter import ttk, messagebox
from db import get_db_connection
from decimal import Decimal


class CashierPanel(tk.Frame):
    def __init__(self, master, switch_frame_callback, current_user_id):
        super().__init__(master, width=800, height=500)
        self.switch_frame = switch_frame_callback
        self.current_user_id = current_user_id
        self.pack_propagate(False)

        self.hardware_categories = ['All', 'CPU', 'RAM', 'Motherboard', 'GPU', 'SSD', 'HDD', 'PSU', 'Case', 'Cooler']
        self.selected_product = None
        self.cart_items = {}

        style = ttk.Style()
        style.configure("Selected.TButton", background="#90ee90", foreground="black")

        side_panel = ttk.Frame(self, width=200)
        side_panel.pack(side="left", fill="y")
        side_panel.pack_propagate(False)

        ttk.Label(side_panel, text="Cashier Menu", font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Button(side_panel, text="Transaction", command=self.new_transaction).pack(pady=5, fill="x", padx=10)
        ttk.Button(side_panel, text="Transaction History", command=self.transaction_history).pack(pady=5, fill="x", padx=10)
        ttk.Button(side_panel, text="Logout", command=lambda: switch_frame_callback("login")).pack(pady=30, fill="x", padx=10)

        self.content_frame = ttk.Frame(self, width=600, height=500)
        self.content_frame.pack(side="right", fill="both", expand=True)
        self.content_frame.pack_propagate(False)

        self.display_welcome()

    def display_welcome(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        ttk.Label(self.content_frame, text="Welcome to the Cashier Panel", font=("Arial", 16)).pack(pady=50)

    def new_transaction(self, filter_category="All"):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.selected_product = None
        product_buttons = []

        button_frame_top = ttk.Frame(self.content_frame)
        button_frame_bottom = ttk.Frame(self.content_frame)
        button_frame_top.pack(pady=(10, 0))
        button_frame_bottom.pack(pady=(5, 10))

        for cat in self.hardware_categories[:5]:
            ttk.Button(button_frame_top, text=cat, command=lambda c=cat: self.new_transaction(c)).pack(side="left", padx=5)
        for cat in self.hardware_categories[5:]:
            ttk.Button(button_frame_bottom, text=cat, command=lambda c=cat: self.new_transaction(c)).pack(side="left", padx=5)

        ttk.Label(self.content_frame, text=f"{filter_category} Products", font=("Arial", 14, "bold")).pack()

        main_area = ttk.Frame(self.content_frame)
        main_area.pack(fill="both", expand=True)

        product_frame = ttk.Frame(main_area)
        product_frame.pack(side="left", fill="both", expand=True, padx=5)

        canvas = tk.Canvas(product_frame)
        scrollbar = ttk.Scrollbar(product_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        cart_frame = ttk.Frame(main_area, relief="solid", padding=10)
        cart_frame.pack(side="right", fill="y", padx=5, pady=5)

        ttk.Label(cart_frame, text="Selected Items", font=("Arial", 12, "bold")).pack()
        self.cart_listbox = tk.Listbox(cart_frame, width=35)
        self.cart_listbox.pack(pady=5)
        self.cart_total_label = ttk.Label(cart_frame, text="Total: ₱0.00", font=("Arial", 11, "bold"))
        self.cart_total_label.pack(pady=5)

        ttk.Button(cart_frame, text="Add to Cart", command=self.add_to_cart).pack(pady=(10, 5))
        ttk.Button(cart_frame, text="Checkout", command=self.checkout_prompt).pack(pady=5)

        self.selected_label = ttk.Label(cart_frame, text="No product selected", font=("Arial", 10))
        self.selected_label.pack(pady=5)

        products = self.get_hardware_products(filter_category)
        if not products:
            ttk.Label(scrollable_frame, text="No products found.", font=("Arial", 12)).pack(pady=10)
            return

        def on_product_click(product, btn):
            self.selected_product = product
            self.selected_label.config(text=f"Selected: {product['name']} (₱{product['price']:.2f})")
            for b in product_buttons:
                b.config(style="TButton")
            btn.config(style="Selected.TButton")

        for index, product in enumerate(products):
            btn_text = f"{product['name']}\n₱{product['price']:.2f}\nStock: {product['stock_quantity']}"
            btn = ttk.Button(scrollable_frame, text=btn_text, width=20)
            btn.grid(row=index // 2, column=index % 2, padx=5, pady=5)
            btn.config(command=lambda p=product, b=btn: on_product_click(p, b))
            product_buttons.append(btn)

    def add_to_cart(self):
        if self.selected_product:
            pid = self.selected_product['product_id']
            if pid in self.cart_items:
                if self.cart_items[pid]['quantity'] < self.selected_product['stock_quantity']:
                    self.cart_items[pid]['quantity'] += 1
                else:
                    messagebox.showwarning("Stock Limit", "Not enough stock available.")
                    return
            else:
                self.cart_items[pid] = {'product': self.selected_product, 'quantity': 1}
            self.refresh_cart_display()

    def refresh_cart_display(self):
        self.cart_listbox.delete(0, tk.END)
        total = 0
        for item in self.cart_items.values():
            p = item['product']
            qty = item['quantity']
            line = f"{p['name']} x{qty} - ₱{p['price'] * qty:.2f}"
            self.cart_listbox.insert(tk.END, line)
            total += p['price'] * qty
        self.cart_total_label.config(text=f"Total: ₱{total:.2f}")

    def checkout_prompt(self):
        if not self.cart_items:
            return

        popup = tk.Toplevel(self)
        popup.title("Checkout")
        popup.geometry("400x400")
        popup.transient(self)

        ttk.Label(popup, text="Order Summary", font=("Arial", 14, "bold")).pack(pady=10)
        listbox = tk.Listbox(popup, width=50)
        listbox.pack(pady=5)

        total = Decimal("0.00")
        for item in self.cart_items.values():
            p = item['product']
            qty = item['quantity']
            price = Decimal(str(p['price'])) * qty
            total += price
            listbox.insert(tk.END, f"{p['name']} x{qty} = ₱{price:.2f}")

        ttk.Label(popup, text=f"Total: ₱{total:.2f}", font=("Arial", 11, "bold")).pack(pady=5)

        frame = ttk.Frame(popup)
        frame.pack(pady=5)

        ttk.Label(frame, text="Payment: ").grid(row=0, column=0, padx=5)
        payment_entry = ttk.Entry(frame)
        payment_entry.grid(row=0, column=1, padx=5)

        change_label = ttk.Label(popup, text="Change: ₱0.00")
        change_label.pack(pady=5)

        def calculate_change(*args):
            try:
                payment = Decimal(payment_entry.get())
                change = payment - total
                if change >= 0:
                    change_label.config(text=f"Change: ₱{change:.2f}")
                else:
                    change_label.config(text="Insufficient Payment")
            except Exception:
                change_label.config(text="Invalid Input")

        payment_entry.bind("<KeyRelease>", calculate_change)

        def confirm_transaction():
            try:
                payment = Decimal(payment_entry.get())
                if payment < total:
                    messagebox.showerror("Payment Error", "Payment is insufficient.")
                    return

                change = payment - total

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO transactions (user_id, total_amount, payment_amount, change_amount, transaction_date) "
                    "VALUES (%s, %s, %s, %s, NOW())",
                    (self.current_user_id, total, payment, change)
                )
                transaction_id = cursor.lastrowid

                for item in self.cart_items.values():
                    p = item['product']
                    qty = item['quantity']
                    unit_price = Decimal(str(p['price']))

                    cursor.execute(
                        "INSERT INTO transaction_items (transaction_id, product_id, quantity, unit_price) "
                        "VALUES (%s, %s, %s, %s)",
                        (transaction_id, p['product_id'], qty, unit_price)
                    )

                    cursor.execute(
                        "UPDATE products SET stock_quantity = stock_quantity - %s "
                        "WHERE product_id = %s AND stock_quantity >= %s",
                        (qty, p['product_id'], qty)
                    )

                conn.commit()
                conn.close()

                self.cart_items.clear()
                self.refresh_cart_display()
                popup.destroy()
                messagebox.showinfo("Success", "Transaction completed successfully.")
                self.new_transaction()

            except Exception as e:
                messagebox.showerror("Error", f"Transaction failed.\n{e}")

        ttk.Button(popup, text="Confirm Payment", command=confirm_transaction).pack(pady=10)

    def transaction_history(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Transaction History", font=("Arial", 14, "bold")).pack(pady=10)

        frame = ttk.Frame(self.content_frame)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        x_scroll = ttk.Scrollbar(frame, orient="horizontal")
        y_scroll = ttk.Scrollbar(frame, orient="vertical")

        tree = ttk.Treeview(
            frame,
            columns=("Transaction ID", "User ID","Date", "Total", "Payment", "Change"),
            show="headings",
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set
        )

        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)
        x_scroll.pack(side="bottom", fill="x")
        y_scroll.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, side="left")

        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT transaction_id, user_id, total_amount, payment_amount, change_amount, transaction_date
                FROM transactions
                WHERE user_id = %s
                ORDER BY transaction_date DESC
            """, (self.current_user_id,))
            transactions = cursor.fetchall()
            conn.close()

            for txn in transactions:
                tree.insert("", "end", values=(
                    txn["transaction_id"],
                    txn["user_id"],
                    txn["transaction_date"].strftime("%Y-%m-%d %H:%M"),
                    f"₱{txn['total_amount']:.2f}",
                    f"₱{txn['payment_amount']:.2f}",
                    f"₱{txn['change_amount']:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions.\n{e}")

    def get_hardware_products(self, filter_category="All"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            categories = ['CPU', 'RAM', 'Motherboard', 'GPU', 'SSD', 'HDD', 'PSU', 'Case', 'Cooler']
            if filter_category == "All":
                placeholders = ', '.join(['%s'] * len(categories))
                query = f"SELECT * FROM products WHERE category IN ({placeholders})"
                cursor.execute(query, categories)
            else:
                query = "SELECT * FROM products WHERE category = %s"
                cursor.execute(query, (filter_category,))
            products = cursor.fetchall()
            conn.close()
            return products
        except Exception as e:
            print("Database error:", e)
            return []
