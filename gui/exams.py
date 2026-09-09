"""
Examinations & Marks Screen for College Management System.
Features score recording, automatic grading calculation (A+ to F), and student report card generation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, Optional

from gui.styles import PALETTE, FONTS
from services.marks_service import MarksService
from database.database import fetch_all
from utils.export import export_marks_to_csv


class ExamsScreen(tk.Frame):
    """
    Exams and Marks management screen.
    """

    def __init__(self, parent, marks_service: MarksService, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.svc = marks_service
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Examinations, Marks & Report Cards", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text="Grading Thresholds: A+ (>=90%), A (>=80%), B+ (>=70%), B (>=60%), C (>=50%), D (>=40%), F (<40%)", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)

        ttk.Button(btn_box, text="📜 View Student Report Card", style="Secondary.TButton", command=self.open_report_card_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="⬇ Export CSV", style="Secondary.TButton", command=self.handle_export).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="+ Record Marks", style="Primary.TButton", command=self.open_record_marks_dialog).pack(side=tk.LEFT, padx=4)

        # Filters Bar
        filter_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        filter_card.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(filter_card, text="Select Exam:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.exam_var = tk.StringVar(value="All Exams")
        self.exam_combo = ttk.Combobox(filter_card, textvariable=self.exam_var, state="readonly", width=28)
        self.exam_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.exam_combo.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        ttk.Button(filter_card, text="Refresh", style="Secondary.TButton", command=self.load_data).pack(side=tk.RIGHT)
        self.count_lbl = tk.Label(filter_card, text="", font=FONTS["small"], fg=PALETTE["primary"], bg=PALETTE["bg_card"])
        self.count_lbl.pack(side=tk.RIGHT, padx=15)

        # Table Card
        table_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        cols = ("roll_no", "name", "exam", "subject", "obtained", "total", "percentage", "grade")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")

        self.tree.heading("roll_no", text="Roll No")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("exam", text="Exam Name")
        self.tree.heading("subject", text="Subject")
        self.tree.heading("obtained", text="Marks Obtained")
        self.tree.heading("total", text="Max Marks")
        self.tree.heading("percentage", text="Percentage")
        self.tree.heading("grade", text="Letter Grade")

        self.tree.column("roll_no", width=80, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("exam", width=160, anchor="w")
        self.tree.column("subject", width=200, anchor="w")
        self.tree.column("obtained", width=110, anchor="center")
        self.tree.column("total", width=90, anchor="center")
        self.tree.column("percentage", width=100, anchor="center")
        self.tree.column("grade", width=90, anchor="center")

        v_scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_exam_combo()

    def _populate_exam_combo(self):
        exams = fetch_all("SELECT exam_id, exam_name FROM exams;", db_path=self.db_path)
        self.exam_map = {"All Exams": None}
        opts = ["All Exams"]
        for e in exams:
            title = f"{e['exam_id']}: {e['exam_name']}"
            self.exam_map[title] = e["exam_id"]
            opts.append(title)
        self.exam_combo["values"] = opts
        self.exam_combo.current(0)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        ex_title = self.exam_var.get()
        ex_id = self.exam_map.get(ex_title)

        query = """
            SELECT m.*, s.roll_no, s.name AS student_name, e.exam_name, e.total_marks, sub.subject_name,
                   ROUND((m.marks_obtained / e.total_marks) * 100, 2) AS pct
            FROM marks m
            JOIN students s ON m.student_id = s.student_id
            JOIN exams e ON m.exam_id = e.exam_id
            JOIN subjects sub ON e.subject_id = sub.subject_id
            WHERE 1=1
        """
        params = []
        if ex_id:
            query += " AND m.exam_id = ?"
            params.append(ex_id)
        query += " ORDER BY s.roll_no ASC, m.marks_obtained DESC;"

        rows = fetch_all(query, tuple(params), db_path=self.db_path)
        from models.exam import Mark

        for r in rows:
            grade, _, _ = Mark.calculate_grade(r["pct"])
            self.tree.insert("", tk.END, values=(
                r["roll_no"],
                r["student_name"],
                r["exam_name"],
                r["subject_name"],
                f"{r['marks_obtained']:.1f}",
                f"{r['total_marks']:.1f}",
                f"{r['pct']:.1f}%",
                grade
            ))

        self.count_lbl.config(text=f"Total Marks Entries: {len(rows)}")

    def open_record_marks_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Record Student Marks")
        dialog.geometry("440x360")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Record / Update Examination Score", font=FONTS["subtitle"], bg=PALETTE["bg_card"], fg=PALETTE["primary"]).pack(anchor="w", pady=(0, 15))

        # Student selector
        students = fetch_all("SELECT student_id, roll_no, name FROM students ORDER BY roll_no ASC;", db_path=self.db_path)
        exams = fetch_all("SELECT exam_id, exam_name, total_marks FROM exams;", db_path=self.db_path)

        stu_opts = [f"{s['student_id']}: {s['roll_no']} - {s['name']}" for s in students]
        exam_opts = [f"{e['exam_id']}: {e['exam_name']} (Max {e['total_marks']})" for e in exams]

        tk.Label(form, text="Student:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        stu_cb = ttk.Combobox(form, values=stu_opts, state="readonly")
        if stu_opts:
            stu_cb.current(0)
        stu_cb.pack(fill=tk.X, pady=(2, 10))

        tk.Label(form, text="Examination:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        exam_cb = ttk.Combobox(form, values=exam_opts, state="readonly")
        if exam_opts:
            exam_cb.current(0)
        exam_cb.pack(fill=tk.X, pady=(2, 10))

        tk.Label(form, text="Marks Obtained:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        score_ent = ttk.Entry(form)
        score_ent.insert(0, "85.0")
        score_ent.pack(fill=tk.X, pady=(2, 12))

        err_lbl = tk.Label(form, text="", font=FONTS["small"], fg=PALETTE["danger"], bg=PALETTE["bg_card"])
        err_lbl.pack(fill=tk.X, pady=(0, 10))

        def save():
            if not stu_cb.get() or not exam_cb.get():
                err_lbl.config(text="Please select student and exam.")
                return
            s_id = int(stu_cb.get().split(":")[0])
            e_id = int(exam_cb.get().split(":")[0])
            try:
                score = float(score_ent.get().strip())
                self.svc.record_mark(s_id, e_id, score)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Success", "Marks recorded and grade updated successfully.")
            except Exception as e:
                err_lbl.config(text=f"Error: {str(e)}")

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="Save Score", style="Primary.TButton", command=save).pack(side=tk.RIGHT)

    def open_report_card_dialog(self):
        """Open Student Report Card generator dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Student Academic Transcript & Report Card")
        dialog.geometry("620x650")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=15, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Student Academic Transcript Generator", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w")

        sel_row = tk.Frame(form, bg=PALETTE["bg_card"])
        sel_row.pack(fill=tk.X, pady=8)

        tk.Label(sel_row, text="Select Student:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT)
        students = fetch_all("SELECT student_id, roll_no, name FROM students ORDER BY roll_no ASC;", db_path=self.db_path)
        stu_opts = [f"{s['student_id']}: {s['roll_no']} - {s['name']}" for s in students]
        stu_combo = ttk.Combobox(sel_row, values=stu_opts, state="readonly", width=35)
        if stu_opts:
            stu_combo.current(0)
        stu_combo.pack(side=tk.LEFT, padx=8)

        transcript_box = tk.Text(form, font=FONTS["code"], bg="#F8FAFC", fg=PALETTE["text_primary"], relief="flat", padx=12, pady=12)
        transcript_box.pack(fill=tk.BOTH, expand=True, pady=10)

        def render_transcript():
            if not stu_combo.get():
                return
            s_id = int(stu_combo.get().split(":")[0])
            report = self.svc.get_student_report_card(s_id)
            stu = report["student"]

            lines = [
                "=" * 64,
                "            OFFICIAL SEMESTER GRADE REPORT",
                "            COLLEGE OF ENGINEERING & TECHNOLOGY",
                "=" * 64,
                f"Student Name : {stu['name']}",
                f"Roll Number  : {stu['roll_no']}",
                f"Semester     : Semester {stu['semester']}",
                "-" * 64,
                f"{'Subject Code':<14} {'Subject Name':<24} {'Score':<8} {'Max':<6} {'Grade':<6}",
                "-" * 64
            ]
            for s in report["subjects"]:
                lines.append(f"{s['subject_code']:<14} {s['subject_name'][:22]:<24} {s['marks_obtained']:<8.1f} {s['total_marks']:<6.0f} {s['grade']:<6}")

            lines.extend([
                "-" * 64,
                f"Total Marks Obtained : {report['total_marks_obtained']:.1f} / {report['total_max_marks']:.1f}",
                f"Aggregate Percentage : {report['overall_percentage']:.2f}%",
                f"Semester GPA (SGPA)  : {report['sgpa']:.2f} / 10.00",
                f"Cumulative Grade     : {report['overall_grade']}",
                f"Result Status        : {report['result_status']}",
                "=" * 64,
                "  Evaluated as per S.E. College Canonical Grading Scale",
                "=" * 64
            ])

            transcript_box.delete("1.0", tk.END)
            transcript_box.insert(tk.END, "\n".join(lines))

        ttk.Button(sel_row, text="Generate Transcript", style="Primary.TButton", command=render_transcript).pack(side=tk.LEFT)
        render_transcript()

    def handle_export(self):
        import os
        export_path = os.path.join(os.getcwd(), "marks_export.csv")
        try:
            count = export_marks_to_csv(export_path, db_path=self.db_path)
            messagebox.showinfo("Export Successful", f"Exported {count} marks records to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
