"""
Marks and Examination Service module for College Management System.
Handles examination creation, score recording, grade calculation (A+ to F),
and student report card generation with SGPA computation.
"""

from typing import Any, Dict, List, Optional, Tuple
from database.database import (
    execute_query, fetch_all, fetch_one, get_student_results_report, DEFAULT_DB_PATH
)
from models.exam import Examination, Mark


class MarksService:
    """
    Manages examinations, marks evaluation, grade assignment,
    and cumulative academic transcripts.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

    def create_exam(self, exam_name: str, subject_id: int, exam_date: str, total_marks: float) -> int:
        """Create an examination with validated maximum marks."""
        exam = Examination(None, exam_name, subject_id, exam_date, total_marks)
        query = """
            INSERT INTO exams (exam_name, subject_id, exam_date, total_marks)
            VALUES (?, ?, ?, ?);
        """
        return execute_query(query, (exam.exam_name, exam.subject_id, exam.exam_date, exam.total_marks), db_path=self.db_path)

    def record_mark(self, student_id: int, exam_id: int, marks_obtained: float) -> int:
        """
        Record score with strict validation:
        1. Marks cannot be negative.
        2. Marks cannot exceed exam's total_marks.
        """
        exam = fetch_one("SELECT * FROM exams WHERE exam_id = ?", (exam_id,), db_path=self.db_path)
        if not exam:
            raise ValueError(f"Exam #{exam_id} not found.")

        total_marks = float(exam["total_marks"])
        score = float(marks_obtained)

        if score < 0:
            raise ValueError(f"Marks obtained cannot be negative (got {score}).")
        if score > total_marks:
            raise ValueError(f"Marks obtained ({score}) cannot exceed maximum exam marks ({total_marks}).")

        query = """
            INSERT INTO marks (student_id, exam_id, marks_obtained)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, exam_id) DO UPDATE SET marks_obtained = excluded.marks_obtained;
        """
        return execute_query(query, (student_id, exam_id, score), db_path=self.db_path)

    def get_student_report_card(self, student_id: int) -> Dict[str, Any]:
        """
        Generate comprehensive academic transcript for a student:
        - All subjects and marks obtained
        - Computed percentage and letter grades
        - Weighted SGPA based on subject credit points
        """
        student = fetch_one("SELECT * FROM students WHERE student_id = ?", (student_id,), db_path=self.db_path)
        if not student:
            raise ValueError(f"Student #{student_id} not found.")

        results = get_student_results_report(student_id=student_id, db_path=self.db_path)
        if not results:
            return {
                "student": dict(student),
                "subjects": [],
                "total_marks_obtained": 0.0,
                "total_max_marks": 0.0,
                "overall_percentage": 0.0,
                "overall_grade": "N/A",
                "sgpa": 0.0,
                "result_status": "No Exams Taken"
            }

        total_obtained = sum(r["marks_obtained"] for r in results)
        total_max = sum(r["total_marks"] for r in results)
        overall_pct = round((total_obtained / total_max) * 100.0, 2) if total_max > 0 else 0.0

        # Calculate grade point for overall percentage
        overall_grade, overall_gp, _ = Mark.calculate_grade(overall_pct)

        # Calculate SGPA (Semester Grade Point Average)
        # Fetch credits for each subject
        total_credits = 0
        weighted_gp = 0.0
        all_passed = True

        for r in results:
            sub = fetch_one("SELECT credits FROM subjects WHERE subject_code = ?", (r["subject_code"],), db_path=self.db_path)
            credits = sub["credits"] if sub else 4
            grade, gp, _ = Mark.calculate_grade(r["percentage"])
            r["credits"] = credits
            r["grade_point"] = gp
            weighted_gp += (gp * credits)
            total_credits += credits
            if grade == "F":
                all_passed = False

        sgpa = round(weighted_gp / total_credits, 2) if total_credits > 0 else 0.0

        return {
            "student": dict(student),
            "subjects": results,
            "total_marks_obtained": total_obtained,
            "total_max_marks": total_max,
            "overall_percentage": overall_pct,
            "overall_grade": overall_grade,
            "sgpa": sgpa,
            "result_status": "PASS" if all_passed else "FAIL (ATKT)"
        }
