"""
Attendance Management Screen for College Management System.
Features batch attendance marking, percentage analytics, and Defaulter warning alerts (<75%).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Any, Dict, List, Optional

from gui.styles import PALETTE, FONTS
from services.attendance_service import AttendanceService
from database.database import fetch_all
from utils.export import export_attendance_to_csv


class AttendanceScreen(tk.Frame):
    """
    Attendance register, batch marking, and defaulters inspection.
    """

    def __init__(self, parent, attendance_service: AttendanceService, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.svc = attendance_service
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Attendance Register & Defaulter Monitor", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text=f"Institutional Threshold: {self.svc.warning_threshold}% | Automated Warning Identification", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)

        ttk.Button(btn_box, text="⬇ Export CSV", style="Secondary.TButton", command=self.handle_export).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="✓ Take Daily Attendance", style="Primary.TButton", command=self.open_mark_dialog).pack(side=tk.LEFT, padx=4)

        # Filters Bar
        filter_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        filter_card.pack(fill=tk.X, padx=20, pady=10)

        # Subject Filter
        tk.Label(filter_card, text="Subject:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.subject_var = tk.StringVar(value="All Subjects")
        self.sub_combo = ttk.Combobox(filter_card, textvariable=self.subject_var, state="readonly", width=30)
        self.sub_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.sub_combo.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        # Defaulter Checkbox Filter
        self.defaulter_only_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(
            filter_card, text="Show Defaulters Only (<75%)", variable=self.defaulter_only_var,
            font=FONTS["body_bold"], fg=PALETTE["danger"], bg=PALETTE["bg_card"],
            activebackground=PALETTE["bg_card"], command=self.load_data
        )
        cb.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(filter_card, text="Refresh", style="Secondary.TButton", command=self.load_data).pack(side=tk.RIGHT)

        self.summary_lbl = tk.Label(filter_card, text="", font=FONTS["small"], fg=PALETTE["primary"], bg=PALETTE["bg_card"])
        self.summary_lbl.pack(side=tk.RIGHT, padx=15)

        # Table Card
        table_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        cols = ("roll_no", "name", "subject", "total", "attended", "missed", "percentage", "status")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")

        self.tree.heading("roll_no", text="Roll No")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("total", text="Total Classes")
        self.tree.heading("attended", text="Attended")
        self.tree.heading("missed", text="Missed")
        self.tree.heading("percentage", text="Attendance %")
        self.tree.heading("status", text="Standing")

        self.tree.column("roll_no", width=80, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("subject", width=220, anchor="w")
        self.tree.column("total", width=90, anchor="center")
        self.tree.column("attended", width=80, anchor="center")
        self.tree.column("missed", width=70, anchor="center")
        self.tree.column("percentage", width=100, anchor="center")
        self.tree.column("status", width=150, anchor="center")

        # Color Tags for Defaulter highlighting
        self.tree.tag_configure("defaulter", background="#FEE2E2", foreground="#991B1B")
        self.tree.tag_configure("satisfactory", background="#FFFFFF", foreground=PALETTE["text_primary"])

        v_scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_subjects_combobox()

    def _populate_subjects_combobox(self):
        subs = fetch_all("SELECT subject_id, subject_code, subject_name FROM subjects ORDER BY subject_name ASC;", db_path=self.db_path)
        self.subject_map = {"All Subjects": None}
        vals = ["All Subjects"]
        for s in subs:
            title = f"{s['subject_code']} - {s['subject_name']}"
            self.subject_map[title] = s["subject_id"]
            vals.append(title)
        self.sub_combo["values"] = vals
        self.sub_combo.current(0)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        selected_title = self.subject_var.get()
        sub_id = self.subject_map.get(selected_title)

        records = self.svc.get_subject_attendance_summary(subject_id=sub_id)

        if self.defaulter_only_var.get():
            records = [r for r in records if r["is_defaulter"]]

        defaulter_count = 0
        for r in records:
            tag = "defaulter" if r["is_defaulter"] else "satisfactory"
            if r["is_defaulter"]:
                defaulter_count += 1

            self.tree.insert("", tk.END, values=(
                r["roll_no"],
                r["student_name"],
                f"{r['subject_code']} - {r['subject_name']}",
                r["total_classes"],
                r["attended_classes"],
                r["missed_classes"],
                f"{r['attendance_percentage']:.1f}%",
                r["status_label"]
            ), tags=(tag,))

        self.summary_lbl.config(
            text=f"Showing: {len(records)} records | ⚠️ Defaulters (<75%): {defaulter_count}"
        )

    def open_mark_dialog(self):
        """Open batch daily attendance marking dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Take Class Attendance")
        dialog.geometry("520x600")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=15, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Daily Attendance Register", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w")

        # Select Subject and Date
        top_row = tk.Frame(form, bg=PALETTE["bg_card"])
        top_row.pack(fill=tk.X, pady=8)

        tk.Label(top_row, text="Subject:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT)
        sub_box = ttk.Combobox(top_row, state="readonly", width=25)
        subs = fetch_all("SELECT subject_id, subject_code, subject_name FROM subjects;", db_path=self.db_path)
        sub_opts = [f"{s['subject_id']}: {s['subject_code']} - {s['subject_name']}" for s in subs]
        sub_box["values"] = sub_opts
        if sub_opts:
            sub_box.current(0)
        sub_box.pack(side=tk.LEFT, padx=6)

        tk.Label(top_row, text="Date:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(10, 4))
        date_ent = ttk.Entry(top_row, width=12)
        date_ent.insert(0, datetime.date.today().isoformat())
        date_ent.pack(side=tk.LEFT)

        # Student checklist frame with scrollbar
        list_frame = tk.Frame(form, bg=PALETTE["bg_card"], highlightbackground=PALETTE["border"], highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        canvas = tk.Canvas(list_frame, bg=PALETTE["bg_card"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=PALETTE["bg_card"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        students = fetch_all("SELECT student_id, roll_no, name FROM students ORDER BY roll_no ASC;", db_path=self.db_path)
        status_vars: Dict[int, tk.StringVar] = {}

        for s in students:
            row = tk.Frame(scrollable_frame, bg=PALETTE["bg_card"], padx=5, pady=3)
            row.pack(fill=tk.X, expand=True)
            tk.Label(row, text=f"{s['roll_no']} — {s['name']}", font=FONTS["small"], bg=PALETTE["bg_card"], width=30, anchor="w").pack(side=tk.LEFT)

            var = tk.StringVar(value="Present")
            status_vars[s["student_id"]] = var

            rb_p = tk.Radiobutton(row, text="Present", variable=var, value="Present", bg=PALETTE["bg_card"], fg=PALETTE["success"])
            rb_a = tk.Radiobutton(row, text="Absent", variable=var, value="Absent", bg=PALETTE["bg_card"], fg=PALETTE["danger"])
            rb_p.pack(side=tk.LEFT, padx=6)
            rb_a.pack(side=tk.LEFT, padx=6)

        # Quick Helper Buttons: "All Present", "All Absent"
        quick_bar = tk.Frame(form, bg=PALETTE["bg_card"])
        quick_bar.pack(fill=tk.X, pady=(0, 10))
        tk.Button(quick_bar, text="Mark All Present", font=FONTS["small"], bg="#ECFDF5", fg=PALETTE["success"], relief="flat",
                  command=lambda: [v.set("Present") for v in status_vars.values()]).pack(side=tk.LEFT, padx=4)
        tk.Button(quick_bar, text="Mark All Absent", font=FONTS["small"], bg="#FEF2F2", fg=PALETTE["danger"], relief="flat",
                  command=lambda: [v.set("Absent") for v in status_vars.values()]).pack(side=tk.LEFT, padx=4)

        def save():
            if not sub_box.get():
                messagebox.showerror("Error", "Please select a subject.")
                return
            sub_id = int(sub_box.get().split(":")[0])
            d_str = date_ent.get().strip()

            try:
                datetime.date.fromisoformat(d_str)
            except ValueError:
                messagebox.showerror("Invalid Date", "Date must be YYYY-MM-DD.")
                return

            att_map = {s_id: var.get() for s_id, var in status_vars.items()}
            count = self.svc.mark_batch_attendance(sub_id, d_str, att_map)
            dialog.destroy()
            self.load_data()
            messagebox.showinfo("Attendance Saved", f"Successfully recorded {count} student attendance records for {d_str}!")

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="Save Attendance", style="Primary.TButton", command=save).pack(side=tk.RIGHT)

    def handle_export(self):
        import os
        selected_title = self.subject_var.get()
        sub_id = self.subject_map.get(selected_title)
        export_path = os.path.join(os.getcwd(), "attendance_export.csv")
        try:
            count = export_attendance_to_csv(export_path, subject_id=sub_id, db_path=self.db_path)
            messagebox.showinfo("Export Successful", f"Exported {count} attendance records to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
