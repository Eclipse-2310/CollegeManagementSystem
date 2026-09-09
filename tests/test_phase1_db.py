"""
Headless verification test suite for Phase 1: Database Layer & Schema.
Asserts:
(a) Clean test DB initialization.
(b) Existence of all 14 tables in sqlite_master.
(c) Foreign keys PRAGMA active and functional (including rejection of invalid FK).
(d) Successful INSERT, SELECT, UPDATE, DELETE cycle on each of the 14 tables.
(e) Parameterized report queries execute without error.
"""

import os
import sys
import sqlite3

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import (
    initialize_database, get_connection, execute_query, fetch_one, fetch_all,
    DatabaseConnection,
    get_students_with_details, get_attendance_percentage_report,
    get_student_results_report, get_department_statistics,
    get_fee_collection_summary, get_library_circulation_summary
)
from database.schema import TABLE_SCHEMAS

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_college.db")


def run_phase1_verification():
    print("=" * 60)
    print("PHASE 1 VERIFICATION: Database Layer & Schema")
    print("=" * 60)

    # Step (a): Clean existing test DB
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"[-] Removed stale test database: {TEST_DB_PATH}")

    # Step (b): Run initialization
    initialize_database(TEST_DB_PATH)
    print(f"[+] Initialized fresh database with schemas and indexes: {TEST_DB_PATH}")

    # Step (c): Assert all 14 tables exist in sqlite_master
    with DatabaseConnection(TEST_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        existing_tables = set(row[0] for row in cursor.fetchall())
        
    expected_tables = set(TABLE_SCHEMAS.keys())
    missing_tables = expected_tables - existing_tables
    assert not missing_tables, f"Missing tables in database: {missing_tables}"
    print(f"[OK] All {len(expected_tables)} required tables verified in sqlite_master:")
    for tbl in sorted(expected_tables):
        print(f"    - {tbl}")

    # Step (d): Assert foreign key pragma enabled and functioning
    with DatabaseConnection(TEST_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys;")
        fk_status = cursor.fetchone()[0]
        assert fk_status == 1, "Foreign keys PRAGMA is not enabled!"
        print("[OK] Foreign keys PRAGMA is actively enabled (1).")

        # Test foreign key enforcement with an invalid FK insertion
        try:
            cursor.execute(
                "INSERT INTO courses (course_name, course_code, department_id, duration) VALUES (?, ?, ?, ?);",
                ("Invalid Course", "INV101", 99999, 4) # department 99999 does not exist
            )
            assert False, "Failed to reject invalid Foreign Key!"
        except sqlite3.IntegrityError:
            print("[OK] Foreign Key constraint enforcement verified (rejected orphan FK).")

    # Step (e): Run INSERT / SELECT / UPDATE / DELETE on each of the 14 tables
    print("\n[+] Testing CRUD cycle across all 14 tables:")

    # 1. users
    uid = execute_query(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        ("test_admin", "hash123", "Admin"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT username FROM users WHERE user_id = ?", (uid,), db_path=TEST_DB_PATH)["username"] == "test_admin"
    execute_query("UPDATE users SET username = ? WHERE user_id = ?", ("admin_renamed", uid), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT username FROM users WHERE user_id = ?", (uid,), db_path=TEST_DB_PATH)["username"] == "admin_renamed"
    print("  [OK] users CRUD verified")

    # 2. departments
    dept_id = execute_query(
        "INSERT INTO departments (department_name, department_code) VALUES (?, ?)",
        ("Computer Science", "CS"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT department_name FROM departments WHERE department_id = ?", (dept_id,), db_path=TEST_DB_PATH)["department_name"] == "Computer Science"
    execute_query("UPDATE departments SET department_name = ? WHERE department_id = ?", ("Computer Engineering", dept_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT department_name FROM departments WHERE department_id = ?", (dept_id,), db_path=TEST_DB_PATH)["department_name"] == "Computer Engineering"
    print("  [OK] departments CRUD verified")

    # 3. courses
    course_id = execute_query(
        "INSERT INTO courses (course_name, course_code, department_id, duration) VALUES (?, ?, ?, ?)",
        ("B.E. Computer Engineering", "BE-CE", dept_id, 4), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT course_name FROM courses WHERE course_id = ?", (course_id,), db_path=TEST_DB_PATH)["course_name"] == "B.E. Computer Engineering"
    execute_query("UPDATE courses SET duration = ? WHERE course_id = ?", (3, course_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT duration FROM courses WHERE course_id = ?", (course_id,), db_path=TEST_DB_PATH)["duration"] == 3
    print("  [OK] courses CRUD verified")

    # 4. faculty
    fac_id = execute_query(
        "INSERT INTO faculty (name, email, phone, department_id, designation) VALUES (?, ?, ?, ?, ?)",
        ("Dr. Alan Turing", "alan@college.edu", "9876543210", dept_id, "Professor"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT designation FROM faculty WHERE faculty_id = ?", (fac_id,), db_path=TEST_DB_PATH)["designation"] == "Professor"
    execute_query("UPDATE faculty SET designation = ? WHERE faculty_id = ?", ("Head of Department", fac_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT designation FROM faculty WHERE faculty_id = ?", (fac_id,), db_path=TEST_DB_PATH)["designation"] == "Head of Department"
    print("  [OK] faculty CRUD verified")

    # 5. students
    stud_id = execute_query(
        """INSERT INTO students 
           (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("CS001", "Ada Lovelace", "Female", "2004-12-10", "ada@college.edu", "9876543211", "London St", dept_id, course_id, 4, 2022),
        db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT name FROM students WHERE student_id = ?", (stud_id,), db_path=TEST_DB_PATH)["name"] == "Ada Lovelace"
    execute_query("UPDATE students SET semester = ? WHERE student_id = ?", (5, stud_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT semester FROM students WHERE student_id = ?", (stud_id,), db_path=TEST_DB_PATH)["semester"] == 5
    print("  [OK] students CRUD verified")

    # 6. subjects
    sub_id = execute_query(
        "INSERT INTO subjects (subject_code, subject_name, credits, semester, course_id, faculty_id) VALUES (?, ?, ?, ?, ?, ?)",
        ("CS401", "Data Structures & Algorithms", 4, 4, course_id, fac_id), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT credits FROM subjects WHERE subject_id = ?", (sub_id,), db_path=TEST_DB_PATH)["credits"] == 4
    execute_query("UPDATE subjects SET credits = ? WHERE subject_id = ?", (5, sub_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT credits FROM subjects WHERE subject_id = ?", (sub_id,), db_path=TEST_DB_PATH)["credits"] == 5
    print("  [OK] subjects CRUD verified")

    # 7. attendance
    att_id = execute_query(
        "INSERT INTO attendance (student_id, subject_id, date, status) VALUES (?, ?, ?, ?)",
        (stud_id, sub_id, "2026-09-01", "Present"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT status FROM attendance WHERE attendance_id = ?", (att_id,), db_path=TEST_DB_PATH)["status"] == "Present"
    execute_query("UPDATE attendance SET status = ? WHERE attendance_id = ?", ("Absent", att_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT status FROM attendance WHERE attendance_id = ?", (att_id,), db_path=TEST_DB_PATH)["status"] == "Absent"
    print("  [OK] attendance CRUD verified")

    # 8. exams
    exam_id = execute_query(
        "INSERT INTO exams (exam_name, subject_id, exam_date, total_marks) VALUES (?, ?, ?, ?)",
        ("Midterm Examination", sub_id, "2026-09-15", 100.0), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT total_marks FROM exams WHERE exam_id = ?", (exam_id,), db_path=TEST_DB_PATH)["total_marks"] == 100.0
    execute_query("UPDATE exams SET total_marks = ? WHERE exam_id = ?", (50.0, exam_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT total_marks FROM exams WHERE exam_id = ?", (exam_id,), db_path=TEST_DB_PATH)["total_marks"] == 50.0
    print("  [OK] exams CRUD verified")

    # 9. marks
    mark_id = execute_query(
        "INSERT INTO marks (student_id, exam_id, marks_obtained) VALUES (?, ?, ?)",
        (stud_id, exam_id, 45.0), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT marks_obtained FROM marks WHERE mark_id = ?", (mark_id,), db_path=TEST_DB_PATH)["marks_obtained"] == 45.0
    execute_query("UPDATE marks SET marks_obtained = ? WHERE mark_id = ?", (48.0, mark_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT marks_obtained FROM marks WHERE mark_id = ?", (mark_id,), db_path=TEST_DB_PATH)["marks_obtained"] == 48.0
    print("  [OK] marks CRUD verified")

    # 10. timetable
    tt_id = execute_query(
        "INSERT INTO timetable (subject_id, faculty_id, day, start_time, end_time, classroom) VALUES (?, ?, ?, ?, ?, ?)",
        (sub_id, fac_id, "Monday", "09:00", "10:00", "LH-101"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT classroom FROM timetable WHERE timetable_id = ?", (tt_id,), db_path=TEST_DB_PATH)["classroom"] == "LH-101"
    execute_query("UPDATE timetable SET classroom = ? WHERE timetable_id = ?", ("LH-102", tt_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT classroom FROM timetable WHERE timetable_id = ?", (tt_id,), db_path=TEST_DB_PATH)["classroom"] == "LH-102"
    print("  [OK] timetable CRUD verified")

    # 11. fees
    fee_id = execute_query(
        """INSERT INTO fees (student_id, total_fee, paid_amount, pending_amount, payment_date, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (stud_id, 50000.0, 30000.0, 20000.0, "2026-08-15", "Partial"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT status FROM fees WHERE fee_id = ?", (fee_id,), db_path=TEST_DB_PATH)["status"] == "Partial"
    execute_query(
        "UPDATE fees SET paid_amount = ?, pending_amount = ?, status = ? WHERE fee_id = ?",
        (50000.0, 0.0, "Paid", fee_id), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT status FROM fees WHERE fee_id = ?", (fee_id,), db_path=TEST_DB_PATH)["status"] == "Paid"
    print("  [OK] fees CRUD verified")

    # 12. library_books
    book_id = execute_query(
        "INSERT INTO library_books (title, author, category, isbn, quantity) VALUES (?, ?, ?, ?, ?)",
        ("Introduction to Algorithms", "CLRS", "Computer Science", "978-0262033848", 5), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT quantity FROM library_books WHERE book_id = ?", (book_id,), db_path=TEST_DB_PATH)["quantity"] == 5
    execute_query("UPDATE library_books SET quantity = ? WHERE book_id = ?", (4, book_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT quantity FROM library_books WHERE book_id = ?", (book_id,), db_path=TEST_DB_PATH)["quantity"] == 4
    print("  [OK] library_books CRUD verified")

    # 13. library_transactions
    trans_id = execute_query(
        "INSERT INTO library_transactions (book_id, student_id, issue_date, status) VALUES (?, ?, ?, ?)",
        (book_id, stud_id, "2026-09-01", "Issued"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT status FROM library_transactions WHERE transaction_id = ?", (trans_id,), db_path=TEST_DB_PATH)["status"] == "Issued"
    execute_query(
        "UPDATE library_transactions SET status = ?, return_date = ? WHERE transaction_id = ?",
        ("Returned", "2026-09-08", trans_id), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT status FROM library_transactions WHERE transaction_id = ?", (trans_id,), db_path=TEST_DB_PATH)["status"] == "Returned"
    print("  [OK] library_transactions CRUD verified")

    # 14. notices
    notice_id = execute_query(
        "INSERT INTO notices (title, description, posted_by, posted_date) VALUES (?, ?, ?, ?)",
        ("Campus Fest 2026", "Annual technical fest dates announced", "Admin", "2026-09-05"), db_path=TEST_DB_PATH
    )
    assert fetch_one("SELECT title FROM notices WHERE notice_id = ?", (notice_id,), db_path=TEST_DB_PATH)["title"] == "Campus Fest 2026"
    execute_query("UPDATE notices SET title = ? WHERE notice_id = ?", ("Annual Tech Fest 2026", notice_id), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT title FROM notices WHERE notice_id = ?", (notice_id,), db_path=TEST_DB_PATH)["title"] == "Annual Tech Fest 2026"
    print("  [OK] notices CRUD verified")

    # Step (f): Verify Parameterized Report Queries
    print("\n[+] Verifying Parameterized Report Queries (DBMS Module):")
    stu_details = get_students_with_details(db_path=TEST_DB_PATH)
    assert len(stu_details) == 1, f"Expected 1 student with details, got {len(stu_details)}"
    print(f"  [OK] JOIN students+departments+courses returned: {stu_details[0]['name']} ({stu_details[0]['department_name']})")

    att_report = get_attendance_percentage_report(db_path=TEST_DB_PATH)
    assert len(att_report) == 1, "Expected 1 attendance record in report"
    print(f"  [OK] Attendance calculation report returned: {att_report[0]['attendance_percentage']}% attendance")

    results_report = get_student_results_report(db_path=TEST_DB_PATH)
    assert len(results_report) == 1, "Expected 1 marks record in report"
    print(f"  [OK] Student results & grades report returned: Grade {results_report[0]['grade']} ({results_report[0]['percentage']}%)")

    dept_stats = get_department_statistics(db_path=TEST_DB_PATH)
    assert len(dept_stats) == 1, "Expected 1 department in statistics"
    print(f"  [OK] Department aggregation statistics returned: {dept_stats[0]['department_name']} (Students: {dept_stats[0]['student_count']})")

    fee_summary = get_fee_collection_summary(db_path=TEST_DB_PATH)
    assert fee_summary["paid_count"] == 1, "Expected 1 paid fee record"
    print(f"  [OK] Fee collection summary returned: Total collected ₹{fee_summary['total_paid_amount']}")

    lib_summary = get_library_circulation_summary(db_path=TEST_DB_PATH)
    assert lib_summary["returned_count"] == 1, "Expected 1 returned book transaction"
    print(f"  [OK] Library circulation summary returned: {lib_summary['unique_titles']} titles, {lib_summary['available_copies']} available copies")

    # Now verify DELETE on child then parent tables (or cascading where configured)
    execute_query("DELETE FROM notices WHERE notice_id = ?", (notice_id,), db_path=TEST_DB_PATH)
    assert fetch_one("SELECT * FROM notices WHERE notice_id = ?", (notice_id,), db_path=TEST_DB_PATH) is None

    execute_query("DELETE FROM library_transactions WHERE transaction_id = ?", (trans_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM library_books WHERE book_id = ?", (book_id,), db_path=TEST_DB_PATH)

    execute_query("DELETE FROM fees WHERE fee_id = ?", (fee_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM marks WHERE mark_id = ?", (mark_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM attendance WHERE attendance_id = ?", (att_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM timetable WHERE timetable_id = ?", (tt_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM exams WHERE exam_id = ?", (exam_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM subjects WHERE subject_id = ?", (sub_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM students WHERE student_id = ?", (stud_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM faculty WHERE faculty_id = ?", (fac_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM courses WHERE course_id = ?", (course_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM departments WHERE department_id = ?", (dept_id,), db_path=TEST_DB_PATH)
    execute_query("DELETE FROM users WHERE user_id = ?", (uid,), db_path=TEST_DB_PATH)
    print("[OK] DELETE verified across all 14 tables.")

    # Clean up test database safely
    import gc
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
            print(f"[-] Cleaned up test database {TEST_DB_PATH}")
        except PermissionError:
            print(f"[!] Note: test database held by OS lock, will be cleaned on next run: {TEST_DB_PATH}")

    print("\n" + "=" * 60)
    print("ALL PHASE 1 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase1_verification()
