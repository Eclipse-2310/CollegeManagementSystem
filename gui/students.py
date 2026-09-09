"""
Students Management Screen for College Management System.
Features searchable Treeview, filters, modal forms, and live Stack-based Undo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional

from gui.styles import PALETTE, FONTS
from services.student_service import StudentService
from models.student import Student
from utils.validation import validate_student_form
from utils.export import export_students_to_csv


class StudentsScreen(tk.Frame):
    """
    Students management screen with search, filters, CRUD, and undo capability.
    """

    def __init__(self, parent, student_service: StudentService, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.svc = student_service
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # Top Header Bar
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Student Directory & Enrollment", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text="Manage enrolled student profiles, contact records, and registration lifecycle", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        # Action Buttons (Right)
        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)

        ttk.Button(btn_box, text="↺ Undo Action", style="Secondary.TButton", command=self.handle_undo).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="⬇ Export CSV", style="Secondary.TButton", command=self.handle_export).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="+ Add Student", style="Primary.TButton", command=self.open_add_dialog).pack(side=tk.LEFT, padx=4)

        # Filter & Search Bar
        filter_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        filter_card.pack(fill=tk.X, padx=20, pady=10)

        # Search box
        tk.Label(filter_card, text="Search:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_data())
        ttk.Entry(filter_card, textvariable=self.search_var, width=28).pack(side=tk.LEFT, padx=(0, 15))

        # Refresh button
        ttk.Button(filter_card, text="Refresh", style="Secondary.TButton", command=self.load_data).pack(side=tk.RIGHT)

        # Status Label
        self.status_lbl = tk.Label(filter_card, text="", font=FONTS["small"], fg=PALETTE["primary"], bg=PALETTE["bg_card"])
        self.status_lbl.pack(side=tk.RIGHT, padx=15)

        # Treeview Table Card
        table_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        columns = ("roll_no", "name", "gender", "email", "phone", "department", "course", "semester", "year")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("roll_no", text="Roll No")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("gender", text="Gender")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("department", text="Department")
        self.tree.heading("course", text="Course")
        self.tree.heading("semester", text="Sem")
        self.tree.heading("year", text="Year")

        self.tree.column("roll_no", width=80, anchor="center")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("gender", width=70, anchor="center")
        self.tree.column("email", width=180, anchor="w")
        self.tree.column("phone", width=110, anchor="center")
        self.tree.column("department", width=160, anchor="w")
        self.tree.column("course", width=160, anchor="w")
        self.tree.column("semester", width=50, anchor="center")
        self.tree.column("year", width=60, anchor="center")

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Context Action row below table
        action_bar = tk.Frame(self, bg=PALETTE["bg_main"])
        action_bar.pack(fill=tk.X, padx=20, pady=(0, 10))

        ttk.Button(action_bar, text="Edit Selected", style="Secondary.TButton", command=self.open_edit_dialog).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(action_bar, text="Delete Selected", style="Danger.TButton", command=self.handle_delete).pack(side=tk.LEFT)

    def load_data(self):
        """Query service and populate Treeview."""
        self.tree.delete(*self.tree.get_children())
        search = self.search_var.get().strip() or None
        students = self.svc.get_all_students(search=search)

        for s in students:
            self.tree.insert("", tk.END, iid=str(s["student_id"]), values=(
                s["roll_no"],
                s["name"],
                s["gender"],
                s["email"],
                s["phone"],
                s["department_name"],
                s["course_name"],
                s["semester"],
                s["admission_year"]
            ))
        self.status_lbl.config(text=f"Total Records: {len(students)}")

    def open_add_dialog(self):
        """Open modal form dialog to register a new student."""
        dialog = tk.Toplevel(self)
        dialog.title("Enroll New Student")
        dialog.geometry("440x520")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="New Student Enrollment Form", font=FONTS["subtitle"], bg=PALETTE["bg_card"], fg=PALETTE["primary"]).pack(anchor="w", pady=(0, 15))

        fields = [
            ("Roll Number:", "roll_no", "CE110"),
            ("Full Name:", "name", "Alan Turing"),
            ("Gender (Male/Female/Other):", "gender", "Male"),
            ("Email Address:", "email", "alan@college.edu"),
            ("Phone Number:", "phone", "9820011999"),
            ("Date of Birth (YYYY-MM-DD):", "dob", "2004-06-15"),
            ("Address:", "address", "Mumbai, India"),
            ("Semester (1-8):", "semester", "1")
        ]

        entries = {}
        for label_text, key, default_val in fields:
            row = tk.Frame(form, bg=PALETTE["bg_card"])
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label_text, font=FONTS["small"], bg=PALETTE["bg_card"], width=22, anchor="w").pack(side=tk.LEFT)
            ent = ttk.Entry(row, font=FONTS["small"])
            ent.insert(0, default_val)
            ent.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entries[key] = ent

        err_label = tk.Label(form, text="", font=FONTS["small"], fg=PALETTE["danger"], bg=PALETTE["bg_card"], wraplength=380)
        err_label.pack(fill=tk.X, pady=6)

        def save():
            data = {
                "roll_no": entries["roll_no"].get().strip(),
                "name": entries["name"].get().strip(),
                "gender": entries["gender"].get().strip(),
                "email": entries["email"].get().strip(),
                "phone": entries["phone"].get().strip(),
                "date_of_birth": entries["dob"].get().strip(),
                "address": entries["address"].get().strip(),
                "semester": entries["semester"].get().strip()
            }
            is_valid, errors = validate_student_form(data)
            if not is_valid:
                err_label.config(text="\n".join(errors.values()))
                return

            try:
                stu = Student(
                    student_id=None,
                    roll_no=data["roll_no"],
                    name=data["name"],
                    gender=data["gender"],
                    date_of_birth=data["date_of_birth"],
                    email=data["email"],
                    phone=data["phone"],
                    address=data["address"],
                    department_id=1,  # Default CE
                    course_id=1,
                    semester=int(data["semester"]),
                    admission_year=2024
                )
                self.svc.add_student(stu, track_undo=True)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Success", f"Enrolled student '{stu.name}' ({stu.roll_no}) successfully!")
            except Exception as e:
                err_label.config(text=f"Enrollment Error: {str(e)}")

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btn_row, text="Save Student", style="Primary.TButton", command=save).pack(side=tk.RIGHT)

    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student record from the table to edit.")
            return

        student_id = int(selected[0])
        student_data = self.svc.get_all_students()
        student = next((s for s in student_data if s["student_id"] == student_id), None)
        if not student:
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Edit Student — {student['name']}")
        dialog.geometry("440x480")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text=f"Update Record: {student['roll_no']}", font=FONTS["subtitle"], bg=PALETTE["bg_card"], fg=PALETTE["primary"]).pack(anchor="w", pady=(0, 15))

        fields = [
            ("Full Name:", "name", student["name"]),
            ("Email Address:", "email", student["email"]),
            ("Phone Number:", "phone", student["phone"]),
            ("Address:", "address", student["address"]),
            ("Semester (1-8):", "semester", str(student["semester"]))
        ]

        entries = {}
        for label_text, key, val in fields:
            row = tk.Frame(form, bg=PALETTE["bg_card"])
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text=label_text, font=FONTS["small"], bg=PALETTE["bg_card"], width=20, anchor="w").pack(side=tk.LEFT)
            ent = ttk.Entry(row, font=FONTS["small"])
            ent.insert(0, str(val))
            ent.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entries[key] = ent

        err_label = tk.Label(form, text="", font=FONTS["small"], fg=PALETTE["danger"], bg=PALETTE["bg_card"], wraplength=380)
        err_label.pack(fill=tk.X, pady=6)

        def update():
            try:
                sem = int(entries["semester"].get().strip())
                if not (1 <= sem <= 8):
                    err_label.config(text="Semester must be between 1 and 8.")
                    return
                updated = {
                    "name": entries["name"].get().strip(),
                    "email": entries["email"].get().strip(),
                    "phone": entries["phone"].get().strip(),
                    "address": entries["address"].get().strip(),
                    "semester": sem
                }
                self.svc.update_student(student_id, updated, track_undo=True)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Updated", f"Updated student profile #{student_id} successfully.")
            except Exception as e:
                err_label.config(text=str(e))

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X, pady=(12, 0))
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btn_row, text="Update Profile", style="Primary.TButton", command=update).pack(side=tk.RIGHT)

    def handle_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student record to delete.")
            return

        student_id = int(selected[0])
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student record?\n(Note: This operation can be undone using the Undo button!)"
        )
        if confirm:
            self.svc.delete_student(student_id, track_undo=True)
            self.load_data()
            messagebox.showinfo("Deleted", "Student record removed. Click 'Undo Action' at any time to restore.")

    def handle_undo(self):
        """Pops and reverts the most recent student action from the Stack."""
        res = self.svc.undo_last_action()
        if res:
            self.load_data()
            messagebox.showinfo("Undo Successful", f"Stack Operation: {res}")
        else:
            messagebox.showinfo("Undo History Empty", "There are no further actions in the undo stack.")

    def handle_export(self):
        """Export current student table to CSV."""
        import os
        export_path = os.path.join(os.getcwd(), "students_export.csv")
        try:
            count = export_students_to_csv(export_path, db_path=self.db_path)
            messagebox.showinfo("Export Successful", f"Exported {count} student records to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export CSV: {str(e)}")
