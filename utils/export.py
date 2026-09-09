"""
File Handling and Data Export/Import utilities for College Management System.
Implements CSV exports for Students, Marks, Attendance, and Fees,
and comprehensive JSON database snapshots using Python standard library csv and json.
"""

import csv
import json
import datetime
import os
from typing import Any, Dict, List, Optional, Tuple

from database.database import (
    fetch_all, get_students_with_details, get_attendance_percentage_report,
    get_student_results_report, DEFAULT_DB_PATH
)
from database.schema import TABLE_SCHEMAS


def export_students_to_csv(target_filepath: str, db_path: Optional[str] = None) -> int:
    """
    Export all student profiles to a CSV file.
    Returns the number of student rows exported.
    """
    students = get_students_with_details(db_path=db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_filepath)), exist_ok=True)

    with open(target_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Student ID", "Roll No", "Name", "Gender", "Date of Birth",
            "Email", "Phone", "Address", "Department", "Course",
            "Semester", "Admission Year"
        ])
        for s in students:
            writer.writerow([
                s["student_id"],
                s["roll_no"],
                s["name"],
                s["gender"],
                s["date_of_birth"],
                s["email"],
                s["phone"],
                s["address"],
                s["department_name"],
                s["course_name"],
                s["semester"],
                s["admission_year"]
            ])

    return len(students)


def export_attendance_to_csv(target_filepath: str, subject_id: Optional[int] = None, db_path: Optional[str] = None) -> int:
    """
    Export calculated attendance report to a CSV file.
    Returns the number of rows exported.
    """
    records = get_attendance_percentage_report(subject_id=subject_id, db_path=db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_filepath)), exist_ok=True)

    with open(target_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Roll No", "Student Name", "Subject Code", "Subject Name",
            "Total Classes", "Attended Classes", "Missed Classes",
            "Attendance Percentage", "Status"
        ])
        for r in records:
            pct = r["attendance_percentage"]
            status = "Defaulter (<75%)" if pct < 75.0 else "Satisfactory"
            writer.writerow([
                r["roll_no"],
                r["student_name"],
                r["subject_code"],
                r["subject_name"],
                r["total_classes"],
                r["attended_classes"],
                r["missed_classes"],
                f"{pct:.2f}%",
                status
            ])

    return len(records)


def export_marks_to_csv(target_filepath: str, exam_id: Optional[int] = None, db_path: Optional[str] = None) -> int:
    """
    Export marks and grades report to a CSV file.
    Returns the number of rows exported.
    """
    records = get_student_results_report(exam_id=exam_id, db_path=db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_filepath)), exist_ok=True)

    with open(target_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Roll No", "Student Name", "Exam Name", "Exam Date",
            "Subject Code", "Subject Name", "Marks Obtained",
            "Total Marks", "Percentage", "Grade"
        ])
        for r in records:
            writer.writerow([
                r["roll_no"],
                r["student_name"],
                r["exam_name"],
                r["exam_date"],
                r["subject_code"],
                r["subject_name"],
                r["marks_obtained"],
                r["total_marks"],
                f"{r['percentage']:.2f}%",
                r["grade"]
            ])

    return len(records)


def export_fees_to_csv(target_filepath: str, db_path: Optional[str] = None) -> int:
    """
    Export financial fee ledger report to a CSV file.
    Returns the number of rows exported.
    """
    query = """
        SELECT f.*, s.roll_no, s.name AS student_name, d.department_name
        FROM fees f
        JOIN students s ON f.student_id = s.student_id
        JOIN departments d ON s.department_id = d.department_id
        ORDER BY s.roll_no ASC;
    """
    records = fetch_all(query, (), db_path=db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_filepath)), exist_ok=True)

    with open(target_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Fee ID", "Roll No", "Student Name", "Department",
            "Total Fee (INR)", "Paid Amount (INR)", "Pending Amount (INR)",
            "Payment Date", "Status"
        ])
        for r in records:
            writer.writerow([
                r["fee_id"],
                r["roll_no"],
                r["student_name"],
                r["department_name"],
                f"{r['total_fee']:.2f}",
                f"{r['paid_amount']:.2f}",
                f"{r['pending_amount']:.2f}",
                r["payment_date"] or "N/A",
                r["status"]
            ])

    return len(records)


def export_database_to_json(target_filepath: str, db_path: Optional[str] = None) -> Dict[str, int]:
    """
    Creates a full institutional JSON backup snapshot containing all 14 tables.
    Includes metadata, timestamp, and record counts.
    Returns: Dict mapping table_name -> record_count
    """
    os.makedirs(os.path.dirname(os.path.abspath(target_filepath)), exist_ok=True)
    snapshot: Dict[str, Any] = {
        "metadata": {
            "system": "College Management System (CMS)",
            "version": "1.0.0-SE-Project",
            "exported_at": datetime.datetime.now().isoformat(),
            "format": "JSON Master Snapshot"
        },
        "tables": {},
        "table_counts": {}
    }

    counts: Dict[str, int] = {}
    for table in TABLE_SCHEMAS.keys():
        rows = fetch_all(f"SELECT * FROM {table};", (), db_path=db_path)
        # Convert sqlite3.Row dicts
        serialized_rows = [dict(r) for r in rows]
        snapshot["tables"][table] = serialized_rows
        counts[table] = len(serialized_rows)

    snapshot["table_counts"] = counts

    with open(target_filepath, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)

    return counts


# Convenient Aliases for reports and UI modules
export_students_csv = export_students_to_csv
export_attendance_csv = export_attendance_to_csv
export_marks_csv = export_marks_to_csv
export_fees_csv = export_fees_to_csv
export_full_backup_json = export_database_to_json

