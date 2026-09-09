"""
Settings and System Administration Screen for College Management System.
Provides:
1. User account management (view accounts, add user, change password with salted SHA-256).
2. Database diagnostics (file location, size, table counts, SQLite version).
3. Maintenance actions (JSON database backup, CSV exports, database re-seeding).
4. Academic project metadata and system specifications.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any, Dict, List, Optional
import os
import sqlite3
import datetime

from gui.styles import PALETTE, FONTS
from database.database import (
    DEFAULT_DB_PATH, fetch_all, fetch_one, execute_query, seed_initial_data
)
from utils.security import hash_password
from utils.export import (
    export_database_to_json, export_students_to_csv, export_attendance_to_csv,
    export_marks_to_csv, export_fees_to_csv
)


class SettingsScreen(tk.Frame):
    """
    Settings, User Management, and System Diagnostics Screen.
    """

    def __init__(self, parent, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.db_path = db_path or DEFAULT_DB_PATH
        self._build_ui()
        self.load_users()
        self.load_diagnostics()

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)

        title_row = tk.Frame(title_box, bg=PALETTE["bg_main"])
        title_row.pack(anchor="w")
        tk.Label(title_row, text="⚙️", font=("Segoe UI", 18), bg=PALETTE["bg_main"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(title_row, text="System Settings & Database Diagnostics", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="User security administration, database diagnostics, and maintenance utilities",
            font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]
        ).pack(anchor="w", pady=(2, 0))

        # Two-column layout
        main_body = tk.Frame(self, bg=PALETTE["bg_main"])
        main_body.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 15))

        # Left Column: User Account Management (Width 55%)
        left_col = tk.Frame(main_body, bg=PALETTE["bg_main"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # User Accounts Card
        user_card = tk.Frame(left_col, bg=PALETTE["bg_card"], padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        user_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        tk.Label(user_card, text="Authorized System User Accounts", font=FONTS["heading"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(anchor="w")
        tk.Label(user_card, text="Role-Based Access Control (RBAC) credentials stored with salted SHA-256 hashes", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        # Users Table
        tree_frame = tk.Frame(user_card, bg=PALETTE["bg_card"])
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("user_id", "username", "role", "created_at")
        self.user_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=5)
        self.user_tree.heading("user_id", text="ID")
        self.user_tree.heading("username", text="Username")
        self.user_tree.heading("role", text="Role")
        self.user_tree.heading("created_at", text="Registered At")

        self.user_tree.column("user_id", width=50, anchor="center")
        self.user_tree.column("username", width=120, anchor="w")
        self.user_tree.column("role", width=90, anchor="center")
        self.user_tree.column("created_at", width=140, anchor="center")

        user_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scroll.set)

        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Add / Change Password Form
        form_frame = tk.LabelFrame(user_card, text=" Add User or Update Password ", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"], padx=10, pady=8)
        form_frame.pack(fill=tk.X)

        f_row = tk.Frame(form_frame, bg=PALETTE["bg_card"])
        f_row.pack(fill=tk.X)

        tk.Label(f_row, text="Username:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 4))
        self.new_user_var = tk.StringVar()
        ttk.Entry(f_row, textvariable=self.new_user_var, width=14, font=FONTS["body"]).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(f_row, text="Password:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 4))
        self.new_pass_var = tk.StringVar()
        ttk.Entry(f_row, textvariable=self.new_pass_var, show="•", width=14, font=FONTS["body"]).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(f_row, text="Role:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 4))
        self.new_role_var = tk.StringVar(value="Faculty")
        ttk.Combobox(f_row, textvariable=self.new_role_var, values=["Admin", "Faculty", "Student"], state="readonly", width=9).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(f_row, text="Save User 💾", style="Primary.TButton", command=self.save_user).pack(side=tk.LEFT)

        # Right Column: Diagnostics, Backups & Maintenance
        right_col = tk.Frame(main_body, bg=PALETTE["bg_main"], width=380)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_col.pack_propagate(False)

        # DB Diagnostics Card
        diag_card = tk.Frame(right_col, bg=PALETTE["bg_card"], padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        diag_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(diag_card, text="Database Diagnostics", font=FONTS["heading"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(anchor="w")

        self.diag_info_frame = tk.Frame(diag_card, bg=PALETTE["bg_card"])
        self.diag_info_frame.pack(fill=tk.X, pady=(8, 0))

        # Maintenance Card
        maint_card = tk.Frame(right_col, bg=PALETTE["bg_card"], padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        maint_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(maint_card, text="Maintenance & Recovery Tools", font=FONTS["heading"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        ttk.Button(maint_card, text="📦 Generate Master JSON Backup", style="Secondary.TButton", command=self.trigger_json_backup).pack(fill=tk.X, pady=3)
        ttk.Button(maint_card, text="📑 Export All CSV Master Sheets", style="Secondary.TButton", command=self.trigger_all_csv).pack(fill=tk.X, pady=3)
        ttk.Button(maint_card, text="🔄 Reset & Re-Seed Database", style="Secondary.TButton", command=self.trigger_reseed).pack(fill=tk.X, pady=3)

        # About Card
        about_card = tk.Frame(right_col, bg="#F8FAFC", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        about_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(about_card, text="🎓 College Management System", font=FONTS["heading"], fg=PALETTE["primary"], bg="#F8FAFC").pack(anchor="w")
        tk.Label(about_card, text="Version 1.0.0 — S.E. Computer Engineering", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F8FAFC").pack(anchor="w")

        specs = [
            ("Core Stack:", "Python 3 Standard Library + Tkinter / TTK"),
            ("Database:", "SQLite 3NF Normalized (14 Tables)"),
            ("Data Structures:", "Stack (Undo), Queue (FIFO), DLL (Notices)"),
            ("AI Architecture:", "Autonomous ReAct Cognitive Agent")
        ]
        for k, v in specs:
            s_row = tk.Frame(about_card, bg="#F8FAFC")
            s_row.pack(fill=tk.X, pady=1)
            tk.Label(s_row, text=f"{k} ", font=FONTS["small"], fg=PALETTE["text_primary"], bg="#F8FAFC").pack(side=tk.LEFT)
            tk.Label(s_row, text=v, font=FONTS["code"], fg=PALETTE["primary"], bg="#F8FAFC").pack(side=tk.LEFT)

    def load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        rows = fetch_all("SELECT user_id, username, role, created_at FROM users ORDER BY user_id ASC;", db_path=self.db_path)
        for r in rows:
            self.user_tree.insert("", tk.END, values=(r["user_id"], r["username"], r["role"], r["created_at"]))

    def load_diagnostics(self):
        for w in self.diag_info_frame.winfo_children():
            w.destroy()

        file_size_kb = 0.0
        if os.path.exists(self.db_path):
            file_size_kb = os.path.getsize(self.db_path) / 1024.0

        # Row counts
        tables = ["students", "faculty", "courses", "subjects", "attendance", "exams", "marks", "fees", "library_books", "notices"]
        counts = {}
        for t in tables:
            try:
                row = fetch_one(f"SELECT COUNT(*) AS c FROM {t};", db_path=self.db_path)
                counts[t] = row["c"] if row else 0
            except Exception:
                counts[t] = 0

        info_lines = [
            ("SQLite Engine:", sqlite3.sqlite_version),
            ("Database File:", os.path.basename(self.db_path)),
            ("Database Size:", f"{file_size_kb:.1f} KB"),
            ("Active Students:", str(counts.get("students", 0))),
            ("Faculty Members:", str(counts.get("faculty", 0))),
            ("Courses & Subjects:", f"{counts.get('courses', 0)} / {counts.get('subjects', 0)}"),
            ("Attendance Records:", str(counts.get("attendance", 0))),
            ("Marks Records:", str(counts.get("marks", 0)))
        ]

        for label, val in info_lines:
            row = tk.Frame(self.diag_info_frame, bg=PALETTE["bg_card"])
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=label, font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT)
            tk.Label(row, text=val, font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(side=tk.RIGHT)

    def save_user(self):
        u = self.new_user_var.get().strip()
        p = self.new_pass_var.get()
        role = self.new_role_var.get()

        if not u or not p:
            messagebox.showwarning("Incomplete Fields", "Please enter both username and password.")
            return

        if len(p) < 4:
            messagebox.showwarning("Short Password", "Password must contain at least 4 characters.")
            return

        hashed = hash_password(p)

        existing = fetch_one("SELECT user_id FROM users WHERE username = ?;", (u,), db_path=self.db_path)
        if existing:
            # Update password
            execute_query("UPDATE users SET password_hash = ?, role = ? WHERE user_id = ?;", (hashed, role, existing["user_id"]), db_path=self.db_path)
            messagebox.showinfo("User Updated", f"Password and role updated for user '{u}'.")
        else:
            # Insert new user
            execute_query("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?);", (u, hashed, role), db_path=self.db_path)
            messagebox.showinfo("User Created", f"New user '{u}' with role '{role}' registered successfully.")

        self.new_user_var.set("")
        self.new_pass_var.set("")
        self.load_users()

    def trigger_json_backup(self):
        target = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"college_backup_{datetime.date.today().isoformat()}.json",
            title="Save JSON Master Database Snapshot"
        )
        if not target:
            return
        try:
            counts = export_database_to_json(target, db_path=self.db_path)
            total = sum(counts.values())
            messagebox.showinfo("Backup Successful", f"Master JSON snapshot generated successfully!\n\nExported {total} records across {len(counts)} relational tables.\nSaved to: {target}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Backup failed: {str(e)}")

    def trigger_all_csv(self):
        out_dir = filedialog.askdirectory(title="Select Directory to Save CSV Exports")
        if not out_dir:
            return
        try:
            s_cnt = export_students_to_csv(os.path.join(out_dir, "students.csv"), db_path=self.db_path)
            a_cnt = export_attendance_to_csv(os.path.join(out_dir, "attendance.csv"), db_path=self.db_path)
            m_cnt = export_marks_to_csv(os.path.join(out_dir, "marks.csv"), db_path=self.db_path)
            f_cnt = export_fees_to_csv(os.path.join(out_dir, "fees.csv"), db_path=self.db_path)

            messagebox.showinfo(
                "Export Complete",
                f"Generated 4 CSV files in:\n{out_dir}\n\n• students.csv ({s_cnt} rows)\n• attendance.csv ({a_cnt} rows)\n• marks.csv ({m_cnt} rows)\n• fees.csv ({f_cnt} rows)"
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"CSV export failed: {str(e)}")

    def trigger_reseed(self):
        confirm = messagebox.askyesno(
            "Confirm Database Re-Seeding",
            "Are you sure you want to reset and re-seed the database with canonical sample records (25 students, 6 faculty, 10 subjects, exams, marks, fees, library)?\n\nExisting records will be refreshed."
        )
        if not confirm:
            return
        try:
            seed_initial_data(self.db_path)
            self.load_users()
            self.load_diagnostics()
            messagebox.showinfo("Database Re-Seeded", "Database re-seeded with complete canonical demo datasets.")
        except Exception as e:
            messagebox.showerror("Re-Seed Error", f"Re-seeding failed: {str(e)}")
