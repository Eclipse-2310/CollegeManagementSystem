"""
DBMS Demonstration Panel for College Management System.
Provides an interactive Academic Viva demonstration screen for:
1. 3NF Relational Schema Architecture across 14 tables.
2. Live Referential Integrity & Constraint Enforcement Lab (PK, FK, CHECK, UNIQUE).
3. Interactive Parameterized SQL Query Studio (JOINs, Aggregations, GROUP BY, HAVING).
4. Normalization (1NF, 2NF, 3NF) & ACID Transaction Guarantees.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional
import time
import sqlite3

from gui.styles import PALETTE, FONTS
from database.database import (
    DEFAULT_DB_PATH, DatabaseConnection, fetch_all, fetch_one, execute_query
)
from database.schema import TABLE_SCHEMAS


class DBMSDemoScreen(tk.Frame):
    """
    Academic Viva demonstration screen for Database Management System (DBMS) concepts.
    """

    def __init__(self, parent, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.db_path = db_path or DEFAULT_DB_PATH
        self._build_ui()

    def _build_ui(self):
        # Header Bar
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)

        title_row = tk.Frame(title_box, bg=PALETTE["bg_main"])
        title_row.pack(anchor="w")
        tk.Label(title_row, text="🗄️", font=("Segoe UI", 18), bg=PALETTE["bg_main"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(title_row, text="DBMS Concepts & Relational Schema Viva Panel", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="3NF Normalization | Strict FK & CHECK Constraints | ACID Transactions | Live SQL Studio",
            font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            header, text="3NF NORMALIZED RELATIONAL DB", font=FONTS["small"],
            fg=PALETTE["success"], bg=PALETTE["success_bg"], padx=10, pady=5
        ).pack(side=tk.RIGHT)

        # Tabbed Notebook
        notebook_frame = tk.Frame(self, bg=PALETTE["bg_main"])
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 15))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Tabs
        self.tab_schema = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_constraints = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_query = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_acid = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)

        self.notebook.add(self.tab_schema, text="  📊 3NF Schema & Table Browser  ")
        self.notebook.add(self.tab_constraints, text="  🛡️ Constraint Enforcement Lab  ")
        self.notebook.add(self.tab_query, text="  💻 Interactive SQL Studio  ")
        self.notebook.add(self.tab_acid, text="  📐 Normalization & ACID Proof  ")

        self._build_schema_tab()
        self._build_constraints_tab()
        self._build_query_tab()
        self._build_acid_tab()

    # ==========================================
    # Tab 1: 3NF Schema & Table Browser
    # ==========================================
    def _build_schema_tab(self):
        # Top selection bar
        sel_bar = tk.Frame(self.tab_schema, bg=PALETTE["bg_card"])
        sel_bar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(sel_bar, text="Select Table (14 Total 3NF Tables):", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 8))

        self.tables_list = list(TABLE_SCHEMAS.keys())
        self.selected_table_var = tk.StringVar(value="students")
        table_cb = ttk.Combobox(sel_bar, textvariable=self.selected_table_var, values=self.tables_list, state="readonly", width=22)
        table_cb.pack(side=tk.LEFT, padx=(0, 15))
        table_cb.bind("<<ComboboxSelected>>", lambda e: self._on_table_selected())

        ttk.Button(sel_bar, text="Inspect Schema & Records", style="Primary.TButton", command=self._on_table_selected).pack(side=tk.LEFT)

        # Info card
        self.table_meta_lbl = tk.Label(sel_bar, text="", font=FONTS["small"], fg=PALETTE["primary"], bg=PALETTE["bg_card"])
        self.table_meta_lbl.pack(side=tk.RIGHT)

        # Split frame: DDL / Schema info on top, live records on bottom
        content_split = tk.Frame(self.tab_schema, bg=PALETTE["bg_card"])
        content_split.pack(fill=tk.BOTH, expand=True)

        # Upper Card: DDL Statement
        ddl_card = tk.Frame(content_split, bg="#0F172A", padx=12, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        ddl_card.pack(fill=tk.X, pady=(0, 12))

        tk.Label(ddl_card, text="DDL SCHEMA DEFINITION & RELATIONAL CONSTRAINTS:", font=FONTS["small"], fg="#94A3B8", bg="#0F172A").pack(anchor="w")

        self.ddl_text = tk.Text(ddl_card, height=6, font=FONTS["code"], bg="#0F172A", fg="#38BDF8", relief="flat", wrap=tk.WORD)
        self.ddl_text.pack(fill=tk.X, pady=(4, 0))

        # Lower Card: Live Records Treeview
        tk.Label(content_split, text="LIVE RECORDS IN TABLE (First 15 Rows):", font=FONTS["heading"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 6))

        tree_frame = tk.Frame(content_split, bg=PALETTE["bg_card"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.schema_tree = ttk.Treeview(tree_frame, show="headings", height=8)
        schema_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.schema_tree.yview)
        schema_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.schema_tree.xview)
        self.schema_tree.configure(yscrollcommand=schema_scroll_y.set, xscrollcommand=schema_scroll_x.set)

        self.schema_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        schema_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        schema_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self._on_table_selected()

    def _on_table_selected(self):
        tbl = self.selected_table_var.get()
        ddl = TABLE_SCHEMAS.get(tbl, "-- Schema not found")

        self.ddl_text.config(state=tk.NORMAL)
        self.ddl_text.delete("1.0", tk.END)
        self.ddl_text.insert("1.0", ddl.strip())
        self.ddl_text.config(state=tk.DISABLED)

        # Clear existing treeview columns
        for item in self.schema_tree.get_children():
            self.schema_tree.delete(item)

        try:
            with DatabaseConnection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({tbl});")
                col_info = cursor.fetchall()
                col_names = [c["name"] for c in col_info]

                cursor.execute(f"SELECT COUNT(*) AS total FROM {tbl};")
                count = cursor.fetchone()["total"]

                cursor.execute(f"SELECT * FROM {tbl} LIMIT 15;")
                rows = cursor.fetchall()

            self.table_meta_lbl.config(text=f"Total Records: {count} | Columns: {len(col_names)}")

            self.schema_tree["columns"] = col_names
            for col in col_names:
                self.schema_tree.heading(col, text=col)
                self.schema_tree.column(col, width=110, anchor="w")

            for r in rows:
                vals = [str(r[c]) if r[c] is not None else "NULL" for c in col_names]
                self.schema_tree.insert("", tk.END, values=vals)

        except Exception as e:
            self.table_meta_lbl.config(text=f"Error: {str(e)}")

    # ==========================================
    # Tab 2: Constraint Enforcement Lab
    # ==========================================
    def _build_constraints_tab(self):
        info_box = tk.Frame(self.tab_constraints, bg="#EEF2FF", padx=12, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(fill=tk.X, pady=(0, 15))

        tk.Label(info_box, text="Relational Constraint Enforcement Lab: PRAGMA foreign_keys = ON", font=FONTS["body_bold"], fg=PALETTE["primary"], bg="#EEF2FF").pack(anchor="w")
        tk.Label(
            info_box,
            text="Proves live SQLite rejection of corrupted records violating Primary Key, Foreign Key, CHECK bounds, or UNIQUE rules.",
            font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#EEF2FF"
        ).pack(anchor="w")

        # Tests grid
        grid_frame = tk.Frame(self.tab_constraints, bg=PALETTE["bg_card"])
        grid_frame.pack(fill=tk.X, pady=(0, 15))

        tests = [
            (
                "1. Orphan Foreign Key Rejection",
                "Attempts to insert a student referencing non-existent Department ID 99999.",
                "Expected: sqlite3.IntegrityError: FOREIGN KEY constraint failed",
                self._test_orphan_fk
            ),
            (
                "2. CHECK Constraint Violation (Semester Range)",
                "Attempts to insert a student with semester = 12 (Allowed: 1 to 8).",
                "Expected: sqlite3.IntegrityError: CHECK constraint failed: semester",
                self._test_check_semester
            ),
            (
                "3. CHECK Constraint Violation (Fee Invariant)",
                "Attempts to insert a fee invoice where paid (₹80k) exceeds total fee (₹50k).",
                "Expected: sqlite3.IntegrityError: CHECK constraint failed: paid_amount <= total_fee",
                self._test_check_fees
            ),
            (
                "4. UNIQUE Constraint Violation",
                "Attempts to register a student with an already existing roll number ('CE101').",
                "Expected: sqlite3.IntegrityError: UNIQUE constraint failed: students.roll_no",
                self._test_unique_roll
            )
        ]

        for idx, (title, desc, exp, cmd) in enumerate(tests):
            card = tk.Frame(grid_frame, bg="#F8FAFC", padx=12, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
            card.pack(fill=tk.X, pady=4)

            top_row = tk.Frame(card, bg="#F8FAFC")
            top_row.pack(fill=tk.X)

            tk.Label(top_row, text=title, font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#F8FAFC").pack(side=tk.LEFT)
            ttk.Button(top_row, text="Trigger Test ⚡", style="Primary.TButton", command=cmd).pack(side=tk.RIGHT)

            tk.Label(card, text=desc, font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F8FAFC").pack(anchor="w", pady=(2, 0))
            tk.Label(card, text=exp, font=FONTS["code"], fg="#64748B", bg="#F8FAFC").pack(anchor="w", pady=(1, 0))

        # Console Output Box
        tk.Label(self.tab_constraints, text="LIVE CONSTRAINTS VERIFICATION TERMINAL:", font=FONTS["heading"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(10, 4))

        self.constraint_console = tk.Text(self.tab_constraints, height=7, font=FONTS["code"], bg="#0F172A", fg="#F8FAFC", relief="flat", padx=10, pady=8, wrap=tk.WORD)
        self.constraint_console.pack(fill=tk.BOTH, expand=True)

        self._log_constraint("DBMS Constraint Lab initialized. Ready to execute boundary validation tests.\n", "#38BDF8")

    def _log_constraint(self, text: str, color: str = "#F8FAFC"):
        self.constraint_console.insert(tk.END, text + "\n")
        self.constraint_console.see(tk.END)

    def _test_orphan_fk(self):
        self._log_constraint("[-] Executing: INSERT INTO students referencing department_id=99999...", "#FBBF24")
        try:
            with DatabaseConnection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO students (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
                       VALUES ('BAD_FK', 'Test', 'Male', '2004-01-01', 'badfk@test.com', '9800000000', 'Mumbai', 99999, 1, 4, 2023);"""
                )
            self._log_constraint("❌ FAILED: Database accepted orphan foreign key without error!", "#EF4444")
        except sqlite3.IntegrityError as e:
            self._log_constraint(f"✅ PASSED (Reflexive Rejection): {type(e).__name__}: {str(e)}", "#34D399")

    def _test_check_semester(self):
        self._log_constraint("[-] Executing: INSERT INTO students with semester=12...", "#FBBF24")
        try:
            with DatabaseConnection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO students (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
                       VALUES ('BAD_SEM', 'Test', 'Male', '2004-01-01', 'badsem@test.com', '9800000000', 'Mumbai', 1, 1, 12, 2023);"""
                )
            self._log_constraint("❌ FAILED: Database accepted out-of-range semester!", "#EF4444")
        except sqlite3.IntegrityError as e:
            self._log_constraint(f"✅ PASSED (CHECK Enforced): {type(e).__name__}: {str(e)}", "#34D399")

    def _test_check_fees(self):
        self._log_constraint("[-] Executing: INSERT INTO fees with paid (₹80k) > total (₹50k)...", "#FBBF24")
        try:
            with DatabaseConnection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO fees (student_id, total_fee, paid_amount, pending_amount, status)
                       VALUES (1, 50000.0, 80000.0, -30000.0, 'Paid');"""
                )
            self._log_constraint("❌ FAILED: Database accepted negative pending amount!", "#EF4444")
        except sqlite3.IntegrityError as e:
            self._log_constraint(f"✅ PASSED (Fee Invariant Enforced): {type(e).__name__}: {str(e)}", "#34D399")

    def _test_unique_roll(self):
        self._log_constraint("[-] Executing: INSERT duplicate roll_no 'CE101'...", "#FBBF24")
        try:
            with DatabaseConnection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO students (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
                       VALUES ('CE101', 'Duplicate Name', 'Male', '2004-01-01', 'dup@test.com', '9800000000', 'Mumbai', 1, 1, 4, 2023);"""
                )
            self._log_constraint("❌ FAILED: Database accepted duplicate roll number!", "#EF4444")
        except sqlite3.IntegrityError as e:
            self._log_constraint(f"✅ PASSED (UNIQUE Roll Enforced): {type(e).__name__}: {str(e)}", "#34D399")

    # ==========================================
    # Tab 3: Interactive SQL Query Studio
    # ==========================================
    def _build_query_tab(self):
        # Preset Query Selector
        top_row = tk.Frame(self.tab_query, bg=PALETTE["bg_card"])
        top_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(top_row, text="Preset Academic Queries:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))

        self.presets = {
            "3-Table JOIN (Students + Dept + Course)": (
                "SELECT s.roll_no, s.name, s.gender, d.department_name, c.course_name, s.semester\n"
                "FROM students s\n"
                "JOIN departments d ON s.department_id = d.department_id\n"
                "JOIN courses c ON s.course_id = c.course_id\n"
                "ORDER BY s.roll_no ASC LIMIT 10;"
            ),
            "Attendance Aggregation (CASE WHEN + GROUP BY)": (
                "SELECT s.roll_no, s.name,\n"
                "       COUNT(a.attendance_id) AS total_classes,\n"
                "       SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended,\n"
                "       ROUND((CAST(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS REAL) / COUNT(a.attendance_id)) * 100, 1) AS attendance_pct\n"
                "FROM students s\n"
                "JOIN attendance a ON s.student_id = a.student_id\n"
                "GROUP BY s.student_id\n"
                "ORDER BY attendance_pct ASC LIMIT 10;"
            ),
            "Exam Results & Canonical Grade Distribution": (
                "SELECT s.roll_no, s.name, e.exam_name, sub.subject_name, m.marks_obtained, e.total_marks,\n"
                "       ROUND((m.marks_obtained / e.total_marks) * 100, 1) AS percentage\n"
                "FROM marks m\n"
                "JOIN students s ON m.student_id = s.student_id\n"
                "JOIN exams e ON m.exam_id = e.exam_id\n"
                "JOIN subjects sub ON e.subject_id = sub.subject_id\n"
                "ORDER BY m.marks_obtained DESC LIMIT 10;"
            ),
            "Fee Collection & Defaulter Breakdown": (
                "SELECT s.roll_no, s.name, d.department_name, f.total_fee, f.paid_amount, f.pending_amount, f.status\n"
                "FROM fees f\n"
                "JOIN students s ON f.student_id = s.student_id\n"
                "JOIN departments d ON s.department_id = d.department_id\n"
                "WHERE f.status != 'Paid'\n"
                "ORDER BY f.pending_amount DESC LIMIT 10;"
            ),
            "Timetable Schedule by Day": (
                "SELECT t.day, t.start_time, t.end_time, t.classroom, s.subject_code, s.subject_name, f.name AS faculty_name\n"
                "FROM timetable t\n"
                "JOIN subjects s ON t.subject_id = s.subject_id\n"
                "JOIN faculty f ON t.faculty_id = f.faculty_id\n"
                "ORDER BY t.day, t.start_time ASC;"
            )
        }

        self.preset_var = tk.StringVar(value="3-Table JOIN (Students + Dept + Course)")
        preset_cb = ttk.Combobox(top_row, textvariable=self.preset_var, values=list(self.presets.keys()), state="readonly", width=42)
        preset_cb.pack(side=tk.LEFT, padx=(0, 12))
        preset_cb.bind("<<ComboboxSelected>>", lambda e: self._load_preset_query())

        ttk.Button(top_row, text="Load Preset", style="Secondary.TButton", command=self._load_preset_query).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(top_row, text="Execute SQL Query ▶", style="Primary.TButton", command=self._execute_sql_studio).pack(side=tk.LEFT)

        # SQL Editor Box
        editor_frame = tk.Frame(self.tab_query, bg="#0F172A", padx=10, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        editor_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(editor_frame, text="SQL STATEMENT (Read-Only SELECT queries):", font=FONTS["small"], fg="#94A3B8", bg="#0F172A").pack(anchor="w")

        self.sql_editor = tk.Text(editor_frame, height=5, font=FONTS["code"], bg="#0F172A", fg="#38BDF8", insertbackground="#FFFFFF", relief="flat")
        self.sql_editor.pack(fill=tk.X, pady=(4, 0))

        # Query Telemetry Bar
        self.query_telemetry_lbl = tk.Label(self.tab_query, text="Ready to execute query.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"])
        self.query_telemetry_lbl.pack(anchor="w", pady=(0, 6))

        # Results Table
        res_frame = tk.Frame(self.tab_query, bg=PALETTE["bg_card"])
        res_frame.pack(fill=tk.BOTH, expand=True)

        self.res_tree = ttk.Treeview(res_frame, show="headings", height=8)
        res_scroll_y = ttk.Scrollbar(res_frame, orient=tk.VERTICAL, command=self.res_tree.yview)
        res_scroll_x = ttk.Scrollbar(res_frame, orient=tk.HORIZONTAL, command=self.res_tree.xview)
        self.res_tree.configure(yscrollcommand=res_scroll_y.set, xscrollcommand=res_scroll_x.set)

        self.res_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        res_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        res_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self._load_preset_query()

    def _load_preset_query(self):
        q = self.presets.get(self.preset_var.get(), "")
        self.sql_editor.delete("1.0", tk.END)
        self.sql_editor.insert("1.0", q)
        self._execute_sql_studio()

    def _execute_sql_studio(self):
        sql = self.sql_editor.get("1.0", tk.END).strip()
        if not sql:
            return

        # Security check: Read-Only enforcement in studio
        prohibited = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
        if any(p in sql.upper().split() for p in prohibited):
            messagebox.showwarning("Security Guardrail", "The Interactive SQL Studio is restricted to read-only SELECT and PRAGMA queries to prevent accidental schema or record destruction.")
            return

        # Clear tree
        for item in self.res_tree.get_children():
            self.res_tree.delete(item)

        try:
            start_t = time.perf_counter()
            with DatabaseConnection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                elapsed_ms = (time.perf_counter() - start_t) * 1000

                if cursor.description:
                    col_names = [d[0] for d in cursor.description]
                else:
                    col_names = []

            self.query_telemetry_lbl.config(
                text=f"✅ Query Executed Successfully | Retrieved: {len(rows)} record(s) | Execution Latency: {elapsed_ms:.2f} ms",
                fg="#059669"
            )

            self.res_tree["columns"] = col_names
            for c in col_names:
                self.res_tree.heading(c, text=c)
                self.res_tree.column(c, width=120, anchor="w")

            for r in rows:
                vals = [str(r[c]) if r[c] is not None else "NULL" for c in col_names]
                self.res_tree.insert("", tk.END, values=vals)

        except Exception as e:
            self.query_telemetry_lbl.config(text=f"❌ SQL Execution Error: {str(e)}", fg=PALETTE["danger"])

    # ==========================================
    # Tab 4: Normalization & ACID Proof
    # ==========================================
    def _build_acid_tab(self):
        # 3NF Normalization Proof Card
        norm_card = tk.Frame(self.tab_acid, bg="#F8FAFC", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        norm_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(norm_card, text="📐 3NF Normalization Architectural Proof", font=FONTS["heading"], fg=PALETTE["primary"], bg="#F8FAFC").pack(anchor="w")

        norm_points = [
            ("1NF (Atomic Attributes):", "Every column contains non-divisible scalar values. Zero repeating groups or comma-separated lists."),
            ("2NF (Full Functional Dependency):", "All tables possess explicit primary keys. In associative tables (marks, attendance), non-key fields depend entirely on the full composite key."),
            ("3NF (Zero Transitive Dependencies):", "Non-prime attributes depend exclusively on the candidate key. For instance, student records link to department_id rather than repeating department_name.")
        ]
        for p_title, p_desc in norm_points:
            p_row = tk.Frame(norm_card, bg="#F8FAFC")
            p_row.pack(fill=tk.X, pady=2)
            tk.Label(p_row, text=f"• {p_title} ", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#F8FAFC").pack(side=tk.LEFT)
            tk.Label(p_row, text=p_desc, font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F8FAFC").pack(side=tk.LEFT)

        # ACID Properties Card
        acid_card = tk.Frame(self.tab_acid, bg="#EEF2FF", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        acid_card.pack(fill=tk.X)

        tk.Label(acid_card, text="🔒 ACID Transactional Guarantees in SQLite", font=FONTS["heading"], fg=PALETTE["primary"], bg="#EEF2FF").pack(anchor="w")

        acid_items = [
            ("Atomicity (All-or-Nothing):", "Implemented via DatabaseConnection context manager. Transactions automatically COMMIT on clean exit or execute ROLLBACK on unhandled exceptions."),
            ("Consistency (Rule Invariants):", "Strict schema constraints (PRAGMA foreign_keys = ON, CHECK constraints, UNIQUE, NOT NULL) reject malformed state transitions."),
            ("Isolation (Concurrent Access):", "SQLite WAL (Write-Ahead Logging) and database-level locking prevent dirty reads and uncommitted updates."),
            ("Durability (Persistent Commits):", "Committed transactions are written and flushed directly to sqlite3 disk storage (college_management.db).")
        ]
        for a_title, a_desc in acid_items:
            a_row = tk.Frame(acid_card, bg="#EEF2FF")
            a_row.pack(fill=tk.X, pady=2)
            tk.Label(a_row, text=f"• {a_title} ", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#EEF2FF").pack(side=tk.LEFT)
            tk.Label(a_row, text=a_desc, font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#EEF2FF").pack(side=tk.LEFT)
