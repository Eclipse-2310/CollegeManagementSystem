"""
Faculty Management Screen for College Management System.
Lists faculty directory, departmental designations, and allocation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, Optional

from gui.styles import PALETTE, FONTS
from database.database import fetch_all, execute_query


class FacultyScreen(tk.Frame):
    """
    Faculty directory management screen.
    """

    def __init__(self, parent, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Faculty Directory & Academic Staff", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text="View teaching staff, subject allocations, and departmental positions", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="+ Add Faculty", style="Primary.TButton", command=self.open_add_dialog).pack(side=tk.LEFT)

        # Search Bar
        filter_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        filter_card.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(filter_card, text="Search Staff:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_data())
        ttk.Entry(filter_card, textvariable=self.search_var, width=28).pack(side=tk.LEFT)

        ttk.Button(filter_card, text="Refresh", style="Secondary.TButton", command=self.load_data).pack(side=tk.RIGHT)

        # Table Card
        table_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        cols = ("id", "name", "designation", "department", "email", "phone")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Faculty Name")
        self.tree.heading("designation", text="Designation")
        self.tree.heading("department", text="Department")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("phone", text="Phone")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("designation", width=160, anchor="w")
        self.tree.column("department", width=180, anchor="w")
        self.tree.column("email", width=200, anchor="w")
        self.tree.column("phone", width=120, anchor="center")

        v_scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        query = """
            SELECT f.*, d.department_name
            FROM faculty f
            JOIN departments d ON f.department_id = d.department_id
            WHERE 1=1
        """
        params = []
        search = self.search_var.get().strip()
        if search:
            query += " AND (f.name LIKE ? OR f.email LIKE ? OR f.designation LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term])
        query += " ORDER BY f.faculty_id ASC;"

        rows = fetch_all(query, tuple(params), db_path=self.db_path)
        for r in rows:
            self.tree.insert("", tk.END, values=(
                r["faculty_id"],
                r["name"],
                r["designation"],
                r["department_name"],
                r["email"],
                r["phone"]
            ))

    def open_add_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Faculty Member")
        dialog.geometry("420x380")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Faculty Registration", font=FONTS["subtitle"], bg=PALETTE["bg_card"], fg=PALETTE["primary"]).pack(anchor="w", pady=(0, 15))

        fields = [
            ("Full Name:", "name", "Prof. Donald Knuth"),
            ("Email Address:", "email", "knuth@college.edu"),
            ("Phone Number:", "phone", "9820019988"),
            ("Designation:", "desig", "Professor")
        ]

        entries = {}
        for label_text, key, val in fields:
            row = tk.Frame(form, bg=PALETTE["bg_card"])
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label_text, font=FONTS["small"], bg=PALETTE["bg_card"], width=18, anchor="w").pack(side=tk.LEFT)
            ent = ttk.Entry(row, font=FONTS["small"])
            ent.insert(0, val)
            ent.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entries[key] = ent

        err_lbl = tk.Label(form, text="", font=FONTS["small"], fg=PALETTE["danger"], bg=PALETTE["bg_card"])
        err_lbl.pack(fill=tk.X, pady=6)

        def save():
            name = entries["name"].get().strip()
            email = entries["email"].get().strip()
            phone = entries["phone"].get().strip()
            desig = entries["desig"].get().strip()

            if not name or not email or not desig:
                err_lbl.config(text="Please fill in all required fields.")
                return

            try:
                execute_query(
                    "INSERT INTO faculty (name, email, phone, department_id, designation) VALUES (?, ?, ?, 1, ?);",
                    (name, email, phone, desig), db_path=self.db_path
                )
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Success", f"Faculty member '{name}' registered successfully.")
            except Exception as e:
                err_lbl.config(text=f"Error: {str(e)}")

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btn_row, text="Register Faculty", style="Primary.TButton", command=save).pack(side=tk.RIGHT)
