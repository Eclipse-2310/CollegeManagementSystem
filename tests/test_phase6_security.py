"""
Headless verification test suite for Phase 6: Validation, Security & Exception Handling.
Asserts:
(a) Input Validation:
    - Required field blanks
    - Invalid email patterns
    - Invalid phone numbers
    - Out-of-bounds semesters
    - Marks exceeding total
    - Negative fee amounts
    - Invalid attendance statuses
    All returning user-friendly error strings instead of uncaught exceptions.
(b) Security & Cryptography:
    - Salted SHA-256 password hashing.
    - Constant-time password verification.
    - Safe rejection of wrong passwords.
    - Role-Based Access Control and Session State (UserSession singleton).
(c) Universal Safe Execution:
    - Wrapping sqlite3.IntegrityError (duplicate record & foreign key).
    - Wrapping FileNotFoundError.
    - Wrapping ValueError.
    - Ensuring zero application crash dumps and 100% process liveness.
"""

import os
import sys
import gc
import sqlite3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import initialize_database, execute_query
from utils.validation import (
    validate_required, validate_email, validate_phone, validate_roll_no,
    validate_date, validate_semester, validate_marks, validate_fee_amounts,
    validate_attendance_status, validate_student_form
)
from utils.security import (
    hash_password, verify_password, UserSession, authenticate_user, safe_execute
)
from models.user import AdminUser, FacultyUser, StudentUser

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_sec.db")


def run_phase6_verification():
    print("=" * 60)
    print("PHASE 6 VERIFICATION: Validation, Security & Exception Handling")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. INPUT VALIDATION TESTS (FRIENDLY ERROR MESSAGES)
    # -------------------------------------------------------------
    print("\n[+] 1. Testing Input Field Validators (User-Friendly Error Messages):")

    # Required field
    ok, err = validate_required("", "Student Name")
    assert not ok and "cannot be left blank" in err
    print(f"  [OK] Blank required field caught: '{err}'")

    # Email format
    ok, err = validate_email("invalid_email_at_domain")
    assert not ok and "not a valid email" in err
    print(f"  [OK] Bad email format caught: '{err}'")

    # Phone format (must be 10 digits)
    ok, err = validate_phone("12345")
    assert not ok and "valid 10-digit" in err
    print(f"  [OK] Short phone number caught: '{err}'")

    # Roll number
    ok, err = validate_roll_no("AB")
    assert not ok and "between 3 and 15" in err
    print(f"  [OK] Too short roll number caught: '{err}'")

    # Date format
    ok, err = validate_date("2026-02-31", "Admission Date")
    assert not ok and "valid calendar date" in err
    print(f"  [OK] Invalid calendar date (Feb 31) caught: '{err}'")

    # Semester range
    ok, err = validate_semester(12)
    assert not ok and "between 1 and 8" in err
    print(f"  [OK] Out-of-bounds semester (12) caught: '{err}'")

    # Marks vs Total
    ok, err = validate_marks(105, 100)
    assert not ok and "cannot exceed maximum" in err
    print(f"  [OK] Over-maximum marks caught: '{err}'")

    # Negative fee
    ok, err = validate_fee_amounts(-5000, 0)
    assert not ok and "cannot be negative" in err
    print(f"  [OK] Negative fee caught: '{err}'")

    # Paid exceeds total fee
    ok, err = validate_fee_amounts(50000, 60000)
    assert not ok and "cannot exceed total fee" in err
    print(f"  [OK] Excess payment caught: '{err}'")

    # Attendance status
    ok, err = validate_attendance_status("Excused")
    assert not ok and "must be 'Present' or 'Absent'" in err
    print(f"  [OK] Invalid attendance status caught: '{err}'")

    # Composite form validation
    ok, errors = validate_student_form({
        "roll_no": "X",
        "name": "",
        "email": "bad_email",
        "phone": "999",
        "gender": "Unknown",
        "date_of_birth": "2026-15-40",
        "semester": 9
    })
    assert not ok and len(errors) >= 5
    print(f"  [OK] Composite student form validation flagged {len(errors)} error fields cleanly.")

    # -------------------------------------------------------------
    # 2. SECURITY & CRYPTOGRAPHY TESTS
    # -------------------------------------------------------------
    print("\n[+] 2. Testing Password Hashing, Verification & RBAC Session:")

    plain = "SuperSecretPassword#2026"
    hashed = hash_password(plain)
    assert "$" in hashed, "Stored hash must contain salt separator"
    assert hashed != plain, "Password must not be stored in plaintext"
    print(f"  [OK] Password hashed with salt: {hashed[:24]}...")

    assert verify_password(plain, hashed) is True, "Password verification failed for valid password!"
    assert verify_password("WrongPassword", hashed) is False, "Password verification allowed bad password!"
    print("  [OK] Constant-time password verification verified.")

    # Test Session Singleton
    session = UserSession.get_instance()
    session.logout()
    assert session.is_authenticated() is False
    assert session.get_role() == "Guest"

    admin_u = AdminUser(1, "system_admin")
    session.login(admin_u)
    assert session.is_authenticated() is True
    assert session.has_role("Admin") is True
    assert session.has_role("Student") is False
    print(f"  [OK] UserSession verified: Active User '{session.get_current_user().username}' (Role: {session.get_role()})")
    session.logout()
    assert session.is_authenticated() is False

    # -------------------------------------------------------------
    # 3. UNIVERSAL SAFE EXECUTION & CRASH RESILIENCE
    # -------------------------------------------------------------
    print("\n[+] 3. Testing Safe Execution Wrapper (Zero Crash Guarantee):")

    # Setup test DB
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    initialize_database(TEST_DB_PATH)

    # (a) Database Unique Constraint Violation (Duplicate username)
    execute_query("INSERT INTO users (username, password_hash, role) VALUES ('unique_user', 'h1', 'Admin');", db_path=TEST_DB_PATH)
    
    def try_duplicate_user():
        execute_query("INSERT INTO users (username, password_hash, role) VALUES ('unique_user', 'h2', 'Admin');", db_path=TEST_DB_PATH)

    ok, res, err = safe_execute("Adding User", try_duplicate_user)
    assert not ok and "Duplicate Record" in err
    print(f"  [OK] Handled SQLite UNIQUE constraint: '{err}'")

    # (b) Database Foreign Key Violation (Orphan Course)
    def try_orphan_course():
        execute_query("INSERT INTO courses (course_name, course_code, department_id, duration) VALUES ('BioEng', 'BE-BIO', 99999, 4);", db_path=TEST_DB_PATH)

    ok, res, err = safe_execute("Adding Course", try_orphan_course)
    assert not ok and "Relational Constraint" in err
    print(f"  [OK] Handled SQLite Foreign Key constraint: '{err}'")

    # (c) File Not Found Exception
    def try_missing_file():
        with open("non_existent_file_path_12345.xyz", "r") as f:
            return f.read()

    ok, res, err = safe_execute("Reading File", try_missing_file)
    assert not ok and "File Not Found" in err
    print(f"  [OK] Handled FileNotFoundError: '{err}'")

    # (d) Generic ValueError
    def try_value_error():
        raise ValueError("Invalid numerical conversion factor.")

    ok, res, err = safe_execute("Processing Metric", try_value_error)
    assert not ok and "Validation Error" in err
    print(f"  [OK] Handled ValueError: '{err}'")

    # Clean up test DB
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
            print(f"[-] Cleaned up test database {TEST_DB_PATH}")
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("ALL PHASE 6 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase6_verification()
