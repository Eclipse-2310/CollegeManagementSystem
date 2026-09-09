"""
Headless verification test suite for Phase 2: OOP Model Layer.
Asserts:
(a) Successful instantiation of all domain classes.
(b) Encapsulation integrity (property getters, setters, and validation rejections).
(c) Polymorphism verification via display_dashboard() on AdminUser, FacultyUser, and StudentUser
    confirming role-distinct structures, access levels, and KPIs.
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User, AdminUser, FacultyUser, StudentUser
from models.student import Student
from models.faculty import Faculty
from models.course import Department, Course
from models.subject import Subject
from models.attendance import Attendance
from models.exam import Examination, Mark
from models.other_models import FeeRecord, LibraryBook, LibraryTransaction, Notice, TimetableSlot


def run_phase2_verification():
    print("=" * 60)
    print("PHASE 2 VERIFICATION: OOP Model Layer")
    print("=" * 60)

    # 1. Abstract Base Class Enforcement
    print("\n[+] Testing OOP Abstraction on User base class:")
    try:
        # Cannot instantiate ABC directly
        User(1, "test", "Admin")
        assert False, "Failed: User ABC should not be directly instantiable!"
    except TypeError:
        print("  [OK] User ABC prevents direct instantiation as expected.")

    # 2. Polymorphism Verification
    print("\n[+] Testing Polymorphic display_dashboard() across user roles:")
    admin = AdminUser(1, "admin_user", "hash1")
    faculty = FacultyUser(2, "faculty_user", faculty_id=10, department="Computer Engineering", password_hash="hash2")
    student = StudentUser(3, "student_user", student_id=100, roll_no="CE101", course_name="B.E. Computer Engineering", semester=4, password_hash="hash3")

    admin_dash = admin.display_dashboard()
    faculty_dash = faculty.display_dashboard()
    student_dash = student.display_dashboard()

    # Verify they are all polymorphic instances of User
    assert isinstance(admin, User)
    assert isinstance(faculty, User)
    assert isinstance(student, User)

    # Verify outputs are completely distinct and role-specific
    assert admin_dash["role"] == "Admin"
    assert faculty_dash["role"] == "Faculty"
    assert student_dash["role"] == "Student"

    assert admin_dash["access_level"] != faculty_dash["access_level"]
    assert faculty_dash["access_level"] != student_dash["access_level"]

    assert "Student Enrollment & Records" in admin_dash["quick_actions"]
    assert "Mark Daily Class Attendance" in faculty_dash["quick_actions"]
    assert "Check Personal Attendance Percentage" in student_dash["quick_actions"]

    print(f"  [OK] Admin Dashboard role: '{admin_dash['role']}' -> Access: '{admin_dash['access_level']}'")
    print(f"  [OK] Faculty Dashboard role: '{faculty_dash['role']}' -> Dept: '{faculty_dash['department']}'")
    print(f"  [OK] Student Dashboard role: '{student_dash['role']}' -> Course: '{student_dash['course']}'")
    print("  [OK] Polymorphism verified: Identical method call yielded role-specific behavior.")

    # 3. Domain Entity Encapsulation & Validation
    print("\n[+] Testing Domain Model Encapsulation & Validation:")

    # Student validation
    s = Student(1, "CS101", "Ada Lovelace", "Female", "2004-12-10", "ada@college.edu", "9876543210", "London", 1, 1, 4, 2022)
    assert s.roll_no == "CS101"
    assert s.semester == 4
    try:
        s.semester = 10  # Out of range 1-8
        assert False, "Should have rejected semester 10"
    except ValueError:
        print("  [OK] Student rejected invalid semester (10).")

    # Faculty validation
    f = Faculty(1, "Dr. Turing", "alan@college.edu", "9876543210", 1, "Professor")
    assert f.name == "Dr. Turing"
    f.designation = "Dean of Engineering"
    assert f.designation == "Dean of Engineering"
    print("  [OK] Faculty encapsulation and setters verified.")

    # Department and Course
    dept = Department(1, "Computer Engineering", "CE")
    course = Course(1, "B.E. Computer Engineering", "BE-CE", 1, 4)
    assert dept.department_code == "CE"
    assert course.duration == 4
    print("  [OK] Department and Course models verified.")

    # Subject
    sub = Subject(1, "CE401", "Database Systems", 4, 4, 1, 1)
    assert sub.credits == 4
    print("  [OK] Subject model verified.")

    # Attendance
    att = Attendance(1, 1, 1, "2026-09-01", "Present")
    assert att.is_present() is True
    att.status = "Absent"
    assert att.is_present() is False
    try:
        att.status = "Late"  # Invalid
        assert False, "Should have rejected status 'Late'"
    except ValueError:
        print("  [OK] Attendance status validation verified.")

    # Examination & Mark (Grading boundary check)
    exam = Examination(1, "Midterm", 1, "2026-09-15", 100.0)
    mark_a_plus = Mark(1, 1, 1, 95.0, 100.0)
    mark_a = Mark(2, 1, 1, 85.0, 100.0)
    mark_b_plus = Mark(3, 1, 1, 75.0, 100.0)
    mark_b = Mark(4, 1, 1, 65.0, 100.0)
    mark_c = Mark(5, 1, 1, 55.0, 100.0)
    mark_d = Mark(6, 1, 1, 45.0, 100.0)
    mark_f = Mark(7, 1, 1, 35.0, 100.0)

    assert mark_a_plus.grade == "A+" and mark_a_plus.grade_point == 10.0
    assert mark_a.grade == "A" and mark_a.grade_point == 9.0
    assert mark_b_plus.grade == "B+" and mark_b_plus.grade_point == 8.0
    assert mark_b.grade == "B" and mark_b.grade_point == 7.0
    assert mark_c.grade == "C" and mark_c.grade_point == 6.0
    assert mark_d.grade == "D" and mark_d.grade_point == 5.0
    assert mark_f.grade == "F" and mark_f.grade_point == 0.0 and mark_f.is_passed is False
    print("  [OK] Exam & Mark grading thresholds verified (A+ down to F).")

    # FeeRecord balance enforcement
    fee = FeeRecord(1, 1, 60000.0, 20000.0)
    assert fee.pending_amount == 40000.0
    assert fee.status == "Partial"
    fee.record_payment(40000.0, "2026-09-02")
    assert fee.pending_amount == 0.0
    assert fee.status == "Paid"
    print("  [OK] FeeRecord balance reconciliation verified.")

    # LibraryBook & Transaction
    book = LibraryBook(1, "Clean Architecture", "Robert Martin", "Software Engineering", "978-0134494166", 3)
    assert book.is_available() is True
    trans = LibraryTransaction(1, 1, 1, "2026-09-01")
    assert trans.status == "Issued"
    trans.mark_returned("2026-09-08")
    assert trans.status == "Returned"
    print("  [OK] LibraryBook and LibraryTransaction lifecycle verified.")

    # Notice
    notice = Notice(1, "Exam Schedule", "Final exams begin Dec 1", "Dean", "2026-09-01")
    assert notice.posted_by == "Dean"
    print("  [OK] Notice model verified.")

    # TimetableSlot overlap logic
    slot1 = TimetableSlot(1, 1, 1, "Monday", "09:00", "11:00", "Room 101")
    slot2_overlap = TimetableSlot(2, 2, 2, "Monday", "10:00", "12:00", "Room 101")
    slot3_no_overlap = TimetableSlot(3, 1, 1, "Monday", "11:00", "13:00", "Room 101")
    slot4_diff_day = TimetableSlot(4, 1, 1, "Tuesday", "09:00", "11:00", "Room 101")

    assert slot1.overlaps_with(slot2_overlap) is True
    assert slot1.overlaps_with(slot3_no_overlap) is False
    assert slot1.overlaps_with(slot4_diff_day) is False
    print("  [OK] TimetableSlot overlap logic verified.")

    print("\n" + "=" * 60)
    print("ALL PHASE 2 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase2_verification()
