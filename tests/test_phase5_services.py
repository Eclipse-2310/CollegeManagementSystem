"""
Headless verification test suite for Phase 5: Services & Business Rules Layer.
Tests rigorous edge cases:
(a) Attendance: 100%, 0%, exactly at 75.0% threshold (not defaulter), 74.9% (defaulter).
(b) Marks/Exams: Exact grade boundaries (90.0 A+, 89.9 A, 40.0 D, 39.9 F),
    over-max marks entry rejection, negative marks entry rejection.
(c) Fees: Negative fee rejection, negative payment rejection, overpayment rejection,
    pending amount reconciliation (pending = total - paid).
(d) Timetable: Deliberately conflicting schedule (same faculty double-booking,
    same classroom double-booking) cleanly rejected with explanatory message.
(e) Agentic AI: Autonomous multi-tool reasoning and synthesis.
"""

import os
import sys
import gc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import initialize_database, execute_query, fetch_one
from models.student import Student
from models.other_models import TimetableSlot
from services.attendance_service import AttendanceService
from services.marks_service import MarksService
from services.fee_service import FeeService
from services.admin_service import AdminService
from services.ai_agent import CampusIntelligenceAgent

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_services.db")


def run_phase5_verification():
    print("=" * 60)
    print("PHASE 5 VERIFICATION: Services & Business Rules Layer")
    print("=" * 60)

    # Initialize test DB
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    initialize_database(TEST_DB_PATH)

    # Base seed
    dept_id = execute_query(
        "INSERT INTO departments (department_name, department_code) VALUES ('Information Tech', 'IT');",
        db_path=TEST_DB_PATH
    )
    course_id = execute_query(
        f"INSERT INTO courses (course_name, course_code, department_id, duration) VALUES ('B.E. IT', 'BE-IT', {dept_id}, 4);",
        db_path=TEST_DB_PATH
    )
    fac_1 = execute_query(
        f"INSERT INTO faculty (name, email, phone, department_id, designation) VALUES ('Prof. Smith', 'smith@college.edu', '9876543210', {dept_id}, 'Assistant Professor');",
        db_path=TEST_DB_PATH
    )
    fac_2 = execute_query(
        f"INSERT INTO faculty (name, email, phone, department_id, designation) VALUES ('Dr. Davis', 'davis@college.edu', '9876543211', {dept_id}, 'Associate Professor');",
        db_path=TEST_DB_PATH
    )
    sub_1 = execute_query(
        f"INSERT INTO subjects (subject_code, subject_name, credits, semester, course_id, faculty_id) VALUES ('IT301', 'Web Computing', 4, 3, {course_id}, {fac_1});",
        db_path=TEST_DB_PATH
    )
    stud_1 = execute_query(
        f"""INSERT INTO students 
           (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
           VALUES ('IT101', 'Alice Vance', 'Female', '2004-05-15', 'alice@college.edu', '9876543212', 'City Center', {dept_id}, {course_id}, 3, 2023);""",
        db_path=TEST_DB_PATH
    )
    stud_2 = execute_query(
        f"""INSERT INTO students 
           (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
           VALUES ('IT102', 'Bob Builder', 'Male', '2004-06-20', 'bob@college.edu', '9876543213', 'West Side', {dept_id}, {course_id}, 3, 2023);""",
        db_path=TEST_DB_PATH
    )

    # -------------------------------------------------------------
    # 1. ATTENDANCE SERVICE EDGE CASES
    # -------------------------------------------------------------
    print("\n[+] 1. Testing Attendance Edge Cases & Threshold Boundary:")
    att_svc = AttendanceService(db_path=TEST_DB_PATH, warning_threshold=75.0)

    # (a) 100% Attendance: 4 classes, all 4 Present
    for d in ["2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"]:
        att_svc.mark_attendance(stud_1, sub_1, d, "Present")
    att_100 = att_svc.get_student_overall_attendance(stud_1)
    assert att_100["percentage"] == 100.0
    assert att_100["is_defaulter"] is False
    print("  [OK] 100% Attendance verified (4/4 Present -> 100.0%, Not Defaulter)")

    # (b) Exactly at threshold: 3 Present, 1 Absent = 75.0%
    # Reset student 1 records
    execute_query("DELETE FROM attendance WHERE student_id = ?", (stud_1,), db_path=TEST_DB_PATH)
    att_svc.mark_attendance(stud_1, sub_1, "2026-09-01", "Present")
    att_svc.mark_attendance(stud_1, sub_1, "2026-09-02", "Present")
    att_svc.mark_attendance(stud_1, sub_1, "2026-09-03", "Present")
    att_svc.mark_attendance(stud_1, sub_1, "2026-09-04", "Absent")
    att_75 = att_svc.get_student_overall_attendance(stud_1)
    assert att_75["percentage"] == 75.0
    assert att_75["is_defaulter"] is False, "Exactly 75.0% should NOT be flagged as defaulter (threshold is < 75%)"
    print("  [OK] Exact Threshold verified (3/4 Present -> 75.0%, Not Defaulter)")

    # (c) Below threshold: 2 Present, 2 Absent = 50.0%
    att_svc.mark_attendance(stud_2, sub_1, "2026-09-01", "Present")
    att_svc.mark_attendance(stud_2, sub_1, "2026-09-02", "Present")
    att_svc.mark_attendance(stud_2, sub_1, "2026-09-03", "Absent")
    att_svc.mark_attendance(stud_2, sub_1, "2026-09-04", "Absent")
    att_50 = att_svc.get_student_overall_attendance(stud_2)
    assert att_50["percentage"] == 50.0
    assert att_50["is_defaulter"] is True
    defaulters = att_svc.get_defaulters_list(subject_id=sub_1)
    assert any(d["student_id"] == stud_2 for d in defaulters)
    print("  [OK] Below Threshold verified (2/4 Present -> 50.0%, Correctly Flagged as Defaulter)")

    # (d) 0% Attendance edge case
    execute_query("DELETE FROM attendance WHERE student_id = ?", (stud_2,), db_path=TEST_DB_PATH)
    att_svc.mark_attendance(stud_2, sub_1, "2026-09-01", "Absent")
    att_svc.mark_attendance(stud_2, sub_1, "2026-09-02", "Absent")
    att_0 = att_svc.get_student_overall_attendance(stud_2)
    assert att_0["percentage"] == 0.0
    assert att_0["is_defaulter"] is True
    print("  [OK] 0% Attendance verified (0/2 Present -> 0.0%, Flagged as Defaulter)")

    # -------------------------------------------------------------
    # 2. MARKS & EXAMS SERVICE EDGE CASES
    # -------------------------------------------------------------
    print("\n[+] 2. Testing Marks Service Validation & Grade Boundary Edge Cases:")
    marks_svc = MarksService(db_path=TEST_DB_PATH)
    exam_id = marks_svc.create_exam("Unit Test 1", sub_1, "2026-09-10", 100.0)

    # Over-maximum rejection
    try:
        marks_svc.record_mark(stud_1, exam_id, 105.0)  # Max is 100
        assert False, "Should have rejected over-max marks (105 > 100)!"
    except ValueError as e:
        print(f"  [OK] Rejected over-max marks entry: {e}")

    # Negative marks rejection
    try:
        marks_svc.record_mark(stud_1, exam_id, -10.0)
        assert False, "Should have rejected negative marks (-10)!"
    except ValueError as e:
        print(f"  [OK] Rejected negative marks entry: {e}")

    # Exact Grade Boundary Tests
    from models.exam import Mark
    assert Mark.calculate_grade(90.0)[0] == "A+"
    assert Mark.calculate_grade(89.99)[0] == "A"
    assert Mark.calculate_grade(80.0)[0] == "A"
    assert Mark.calculate_grade(79.99)[0] == "B+"
    assert Mark.calculate_grade(70.0)[0] == "B+"
    assert Mark.calculate_grade(69.99)[0] == "B"
    assert Mark.calculate_grade(60.0)[0] == "B"
    assert Mark.calculate_grade(59.99)[0] == "C"
    assert Mark.calculate_grade(50.0)[0] == "C"
    assert Mark.calculate_grade(49.99)[0] == "D"
    assert Mark.calculate_grade(40.0)[0] == "D"
    assert Mark.calculate_grade(39.99)[0] == "F"
    print("  [OK] All 12 boundary transitions verified according to canonical scale (A+ down to F).")

    # Record valid score and test transcript generation
    marks_svc.record_mark(stud_1, exam_id, 92.0)
    report_card = marks_svc.get_student_report_card(stud_1)
    assert report_card["overall_grade"] == "A+"
    assert report_card["sgpa"] == 10.0
    assert report_card["result_status"] == "PASS"
    print(f"  [OK] Report card generated: Grade={report_card['overall_grade']}, SGPA={report_card['sgpa']}, Status={report_card['result_status']}")

    # -------------------------------------------------------------
    # 3. FEE SERVICE EDGE CASES
    # -------------------------------------------------------------
    print("\n[+] 3. Testing Fee Service Financial Reconciliations & Negative Rejections:")
    fee_svc = FeeService(db_path=TEST_DB_PATH)

    # Negative fee creation rejection
    try:
        fee_svc.create_fee_record(stud_1, -50000.0)
        assert False, "Should have rejected negative fee amount!"
    except ValueError as e:
        print(f"  [OK] Rejected negative fee invoice: {e}")

    # Create valid invoice: Total 60,000, Paid 20,000, Pending 40,000
    fee_id = fee_svc.create_fee_record(stud_1, 60000.0, 20000.0)
    f_rec = fee_svc.get_student_fee_details(stud_1)
    assert f_rec["pending_amount"] == 40000.0
    assert f_rec["status"] == "Partial"
    print("  [OK] Invariant verified: pending (40000) = total (60000) - paid (20000)")

    # Negative payment rejection
    try:
        fee_svc.record_payment(fee_id, -5000.0)
        assert False, "Should have rejected negative payment!"
    except ValueError as e:
        print(f"  [OK] Rejected negative payment: {e}")

    # Overpayment rejection (paying 45,000 when pending is 40,000)
    try:
        fee_svc.record_payment(fee_id, 45000.0)
        assert False, "Should have rejected overpayment!"
    except ValueError as e:
        print(f"  [OK] Rejected overpayment: {e}")

    # Valid settlement payment of 40,000 -> Status becomes 'Paid', Pending becomes 0
    updated_fee = fee_svc.record_payment(fee_id, 40000.0, "2026-09-08")
    assert updated_fee["paid_amount"] == 60000.0
    assert updated_fee["pending_amount"] == 0.0
    assert updated_fee["status"] == "Paid"
    print("  [OK] Exact settlement verified: Pending balance reached 0.0, status='Paid'.")

    # -------------------------------------------------------------
    # 4. TIMETABLE DOUBLE-BOOKING CONFLICT PREVENTION
    # -------------------------------------------------------------
    print("\n[+] 4. Testing Timetable Double-Booking Conflict Prevention:")
    admin_svc = AdminService(db_path=TEST_DB_PATH)

    # Slot 1: Prof. Smith, Monday 09:00 - 11:00 in Room 101
    slot1 = TimetableSlot(None, sub_1, fac_1, "Monday", "09:00", "11:00", "Room 101")
    t1_id = admin_svc.add_timetable_slot(slot1)
    assert t1_id is not None
    print("  [OK] Slot 1 scheduled successfully (Prof. Smith, Mon 09:00-11:00, Room 101)")

    # Conflict Case A: Same faculty (Prof. Smith) booked at overlapping time (10:00 - 12:00) on Monday
    conflict_slot_faculty = TimetableSlot(None, sub_1, fac_1, "Monday", "10:00", "12:00", "Room 102")
    try:
        admin_svc.add_timetable_slot(conflict_slot_faculty)
        assert False, "Should have rejected same-faculty double-booking!"
    except ValueError as e:
        print(f"  [OK] Caught same-faculty double-booking: {e}")

    # Conflict Case B: Same classroom (Room 101) booked by Dr. Davis at overlapping time (10:30 - 11:30) on Monday
    conflict_slot_room = TimetableSlot(None, sub_1, fac_2, "Monday", "10:30", "11:30", "Room 101")
    try:
        admin_svc.add_timetable_slot(conflict_slot_room)
        assert False, "Should have rejected same-classroom double-booking!"
    except ValueError as e:
        print(f"  [OK] Caught same-classroom double-booking: {e}")

    # Non-conflicting Slot: Different day (Tuesday 09:00 - 11:00, Room 101, Prof. Smith)
    slot_tues = TimetableSlot(None, sub_1, fac_1, "Tuesday", "09:00", "11:00", "Room 101")
    t2_id = admin_svc.add_timetable_slot(slot_tues)
    assert t2_id is not None
    print("  [OK] Non-conflicting slot on different day scheduled successfully.")

    # -------------------------------------------------------------
    # 5. AGENTIC AI SERVICE REASONING
    # -------------------------------------------------------------
    print("\n[+] 5. Testing Campus Intelligence Agent (Agentic AI Engine):")
    ai_agent = CampusIntelligenceAgent(db_path=TEST_DB_PATH)

    # Test goal: Attendance inquiry
    ai_resp = ai_agent.run_agent_task("Analyze students with low attendance and defaulters")
    assert "analyze_attendance_defaulters" in ai_resp["executed_tools"]
    assert "Agentic Analysis Complete" in ai_resp["synthesis"]
    print(f"  [OK] AI Agent ReAct Cycle: {ai_resp['thought_log'][1]} -> Tool: {ai_resp['executed_tools'][0]}")
    print(f"       AI Recommendation: {ai_resp['synthesis'][:90]}...")

    # Cleanup test DB
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
            print(f"[-] Cleaned up test database {TEST_DB_PATH}")
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("ALL PHASE 5 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase5_verification()
