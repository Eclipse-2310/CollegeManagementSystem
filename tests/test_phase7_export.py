"""
Headless verification test suite for Phase 7: File Handling (CSV & JSON).
Asserts:
(a) CSV Export of Students: Generated CSV row count matches DB student count.
(b) CSV Export of Attendance: Generated CSV matches DB attendance summary count.
(c) CSV Export of Marks & Grades: Generated CSV matches DB exam marks count.
(d) CSV Export of Fees: Generated CSV matches DB fees ledger count.
(e) JSON Master Backup Snapshot: Re-opened JSON file contains all 14 tables and exact record counts.
"""

import os
import sys
import csv
import json
import gc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import initialize_database, execute_query, fetch_all
from utils.export import (
    export_students_to_csv, export_attendance_to_csv, export_marks_to_csv,
    export_fees_to_csv, export_database_to_json
)

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_export.db")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_exports")


def run_phase7_verification():
    print("=" * 60)
    print("PHASE 7 VERIFICATION: File Handling (CSV / JSON)")
    print("=" * 60)

    # Clean previous artifacts
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    initialize_database(TEST_DB_PATH)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Populate realistic sample records
    dept_id = execute_query("INSERT INTO departments (department_name, department_code) VALUES ('Computer Engg', 'CE');", db_path=TEST_DB_PATH)
    course_id = execute_query(f"INSERT INTO courses (course_name, course_code, department_id, duration) VALUES ('B.E. Computer', 'BE-CE', {dept_id}, 4);", db_path=TEST_DB_PATH)
    fac_id = execute_query(f"INSERT INTO faculty (name, email, phone, department_id, designation) VALUES ('Dr. Turing', 'alan@college.edu', '9876543210', {dept_id}, 'HOD');", db_path=TEST_DB_PATH)
    sub_id = execute_query(f"INSERT INTO subjects (subject_code, subject_name, credits, semester, course_id, faculty_id) VALUES ('CE401', 'OS', 4, 4, {course_id}, {fac_id});", db_path=TEST_DB_PATH)
    exam_id = execute_query(f"INSERT INTO exams (exam_name, subject_id, exam_date, total_marks) VALUES ('Midterm', {sub_id}, '2026-09-10', 100.0);", db_path=TEST_DB_PATH)

    # Add 3 students with attendance, marks, and fees
    for i in range(1, 4):
        s_id = execute_query(
            f"""INSERT INTO students 
               (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
               VALUES ('CE10{i}', 'Student_{i}', 'Male', '2004-01-0{i}', 's{i}@college.edu', '987654321{i}', 'Campus Road', {dept_id}, {course_id}, 4, 2023);""",
            db_path=TEST_DB_PATH
        )
        # Attendance
        execute_query(f"INSERT INTO attendance (student_id, subject_id, date, status) VALUES ({s_id}, {sub_id}, '2026-09-01', 'Present');", db_path=TEST_DB_PATH)
        # Marks
        execute_query(f"INSERT INTO marks (student_id, exam_id, marks_obtained) VALUES ({s_id}, {exam_id}, {80 + i * 5});", db_path=TEST_DB_PATH)
        # Fee
        execute_query(f"INSERT INTO fees (student_id, total_fee, paid_amount, pending_amount, payment_date, status) VALUES ({s_id}, 50000.0, 30000.0, 20000.0, '2026-08-15', 'Partial');", db_path=TEST_DB_PATH)

    # 1. Test Students CSV Export
    print("\n[+] 1. Testing Students CSV Export:")
    stu_csv_path = os.path.join(OUTPUT_DIR, "students_export.csv")
    exported_count = export_students_to_csv(stu_csv_path, db_path=TEST_DB_PATH)
    assert exported_count == 3

    with open(stu_csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        header = reader[0]
        data_rows = reader[1:]
        assert "Roll No" in header and "Name" in header
        assert len(data_rows) == 3
        print(f"  [OK] Students CSV verified: {len(data_rows)} data rows match 3 DB student records.")
        print(f"       Header: {header[:5]}...")

    # 2. Test Attendance CSV Export
    print("\n[+] 2. Testing Attendance CSV Export:")
    att_csv_path = os.path.join(OUTPUT_DIR, "attendance_export.csv")
    exported_att = export_attendance_to_csv(att_csv_path, db_path=TEST_DB_PATH)
    assert exported_att == 3

    with open(att_csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        data_rows = reader[1:]
        assert len(data_rows) == 3
        print(f"  [OK] Attendance CSV verified: {len(data_rows)} data rows match DB records.")

    # 3. Test Marks CSV Export
    print("\n[+] 3. Testing Marks CSV Export:")
    marks_csv_path = os.path.join(OUTPUT_DIR, "marks_export.csv")
    exported_marks = export_marks_to_csv(marks_csv_path, db_path=TEST_DB_PATH)
    assert exported_marks == 3

    with open(marks_csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        data_rows = reader[1:]
        assert len(data_rows) == 3
        print(f"  [OK] Marks CSV verified: {len(data_rows)} data rows match DB records.")

    # 4. Test Fees CSV Export
    print("\n[+] 4. Testing Fees CSV Export:")
    fees_csv_path = os.path.join(OUTPUT_DIR, "fees_export.csv")
    exported_fees = export_fees_to_csv(fees_csv_path, db_path=TEST_DB_PATH)
    assert exported_fees == 3

    with open(fees_csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        data_rows = reader[1:]
        assert len(data_rows) == 3
        print(f"  [OK] Fees CSV verified: {len(data_rows)} data rows match DB records.")

    # 5. Test JSON Master Database Snapshot
    print("\n[+] 5. Testing JSON Master Database Snapshot Export:")
    json_path = os.path.join(OUTPUT_DIR, "database_backup.json")
    counts = export_database_to_json(json_path, db_path=TEST_DB_PATH)

    with open(json_path, "r", encoding="utf-8") as f:
        backup = json.load(f)

    assert "metadata" in backup
    assert "tables" in backup
    assert len(backup["tables"]) == 14, "JSON snapshot should contain all 14 tables"
    assert len(backup["tables"]["students"]) == 3
    assert len(backup["tables"]["fees"]) == 3
    assert len(backup["tables"]["marks"]) == 3
    print(f"  [OK] JSON Snapshot verified across all 14 tables:")
    for t_name, count in counts.items():
        if count > 0:
            print(f"       - {t_name}: {count} records")

    # Clean up test files
    gc.collect()
    for f_name in os.listdir(OUTPUT_DIR):
        try:
            os.remove(os.path.join(OUTPUT_DIR, f_name))
        except Exception:
            pass
    try:
        os.rmdir(OUTPUT_DIR)
    except Exception:
        pass

    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
            print(f"[-] Cleaned up test database {TEST_DB_PATH}")
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("ALL PHASE 7 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase7_verification()
