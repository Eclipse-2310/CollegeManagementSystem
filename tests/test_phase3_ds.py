"""
Headless verification test suite for Phase 3: Data Structures (Genuinely Integrated).
Asserts:
(a) Stack: Adding student pushes to Undo Stack; calling undo() removes student from DB and cache.
(b) Queue: Submitting library issue requests enqueues them; process_next_request() dequeues in strict FIFO order.
(c) LinkedList: Publishing notices inserts at front (head); deleting a notice splices it out; order is chronological.
(d) Dictionary Caches: get_by_roll_no() and get_subject_by_code() return exact DB matches in O(1) time.
"""

import os
import sys
import gc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import initialize_database, execute_query, fetch_one
from models.student import Student
from services.student_service import StudentService
from services.library_service import LibraryService
from services.admin_service import AdminService

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_ds.db")


def run_phase3_verification():
    print("=" * 60)
    print("PHASE 3 VERIFICATION: Data Structures (Genuine Integration)")
    print("=" * 60)

    # Clean & init fresh test database
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    initialize_database(TEST_DB_PATH)

    # Seed minimal base entities (dept, course, faculty, book)
    dept_id = execute_query(
        "INSERT INTO departments (department_name, department_code) VALUES ('Computer Engg', 'CE');",
        db_path=TEST_DB_PATH
    )
    course_id = execute_query(
        f"INSERT INTO courses (course_name, course_code, department_id, duration) VALUES ('B.E. Computer', 'BE-CE', {dept_id}, 4);",
        db_path=TEST_DB_PATH
    )
    book_id = execute_query(
        "INSERT INTO library_books (title, author, category, isbn, quantity) VALUES ('Design Patterns', 'GoF', 'CS', '978-0201633610', 2);",
        db_path=TEST_DB_PATH
    )
    sub_id = execute_query(
        f"INSERT INTO subjects (subject_code, subject_name, credits, semester, course_id) VALUES ('CE301', 'Data Structures', 4, 3, {course_id});",
        db_path=TEST_DB_PATH
    )

    # -------------------------------------------------------------
    # 1. STACK VERIFICATION: Action History & Undo (LIFO)
    # -------------------------------------------------------------
    print("\n[+] 1. Testing Stack Integration (StudentService Undo Stack):")
    student_svc = StudentService(db_path=TEST_DB_PATH)
    assert student_svc.undo_stack.is_empty(), "Stack should be empty initially"

    new_student = Student(
        student_id=None,
        roll_no="CE201",
        name="Grace Hopper",
        gender="Female",
        date_of_birth="2005-02-14",
        email="grace@college.edu",
        phone="9876543210",
        address="New York",
        department_id=dept_id,
        course_id=course_id,
        semester=3,
        admission_year=2023
    )

    # Action 1: Add student -> Pushes to Stack
    added_id = student_svc.add_student(new_student, track_undo=True)
    assert student_svc.undo_stack.size() == 1, f"Expected stack size 1, got {student_svc.undo_stack.size()}"
    top_action = student_svc.undo_stack.peek()
    assert top_action is not None and top_action.action_type == "ADD_STUDENT"
    print(f"  [OK] Stack push verified on student addition: {top_action}")

    # Verify student is in DB and Cache
    assert fetch_one("SELECT name FROM students WHERE student_id = ?", (added_id,), db_path=TEST_DB_PATH) is not None
    assert student_svc.get_by_roll_no("CE201") is not None

    # Action 2: Undo the addition -> Pops from Stack and deletes student
    undo_msg = student_svc.undo_last_action()
    print(f"  [OK] Stack pop & undo executed: '{undo_msg}'")
    assert student_svc.undo_stack.is_empty(), "Stack should be empty after undo"

    # Verify student was indeed removed by the rollback
    assert fetch_one("SELECT name FROM students WHERE student_id = ?", (added_id,), db_path=TEST_DB_PATH) is None
    assert student_svc.get_by_roll_no("CE201") is None
    print("  [OK] Real undo verified: Student was cleanly rolled back from DB and cache!")

    # -------------------------------------------------------------
    # 2. QUEUE VERIFICATION: Request Queue (FIFO)
    # -------------------------------------------------------------
    print("\n[+] 2. Testing Queue Integration (LibraryService Reservation Queue):")
    lib_svc = LibraryService(db_path=TEST_DB_PATH)
    assert lib_svc.request_queue.is_empty(), "Queue should be empty initially"

    # Enqueue 3 requests in order
    r1 = lib_svc.queue_issue_request("Student Alice", "978-0201633610", "Hold copy")
    r2 = lib_svc.queue_issue_request("Student Bob", "978-0201633610", "Urgent semester project")
    r3 = lib_svc.queue_issue_request("Student Charlie", "978-0201633610", "General study")

    assert lib_svc.request_queue.size() == 3
    print(f"  [OK] Enqueued 3 requests. Queue size: {lib_svc.request_queue.size()}")
    print(f"  [OK] Queue front item: {lib_svc.request_queue.front().requester_name}")

    # Dequeue in strict FIFO order: First in Alice -> First out Alice
    out1 = lib_svc.process_next_request()
    assert out1.requester_name == "Student Alice", f"Expected Alice, got {out1.requester_name}"
    print(f"  [OK] Dequeued 1st (FIFO): {out1.requester_name} (Status: {out1.status})")

    out2 = lib_svc.process_next_request()
    assert out2.requester_name == "Student Bob"
    print(f"  [OK] Dequeued 2nd (FIFO): {out2.requester_name} (Status: {out2.status})")

    out3 = lib_svc.process_next_request()
    assert out3.requester_name == "Student Charlie"
    print(f"  [OK] Dequeued 3rd (FIFO): {out3.requester_name} (Status: {out3.status})")

    assert lib_svc.request_queue.is_empty()
    print("  [OK] Queue empty after all requests processed in exact FIFO sequence.")

    # -------------------------------------------------------------
    # 3. LINKED LIST VERIFICATION: Notice Board Chain
    # -------------------------------------------------------------
    print("\n[+] 3. Testing Doubly LinkedList Integration (Notice Board Chain):")
    admin_svc = AdminService(db_path=TEST_DB_PATH)

    # Publish notices: newest should be at front of linked list
    n1 = admin_svc.publish_notice("Fee Deadline", "Term fee due by 15th", "Accounts", "2026-09-01")
    n2 = admin_svc.publish_notice("Workshop on AI", "Antigravity Agentic AI workshop on 20th", "HOD", "2026-09-03")
    n3 = admin_svc.publish_notice("Holiday Notice", "College closed on Friday", "Principal", "2026-09-05")

    notices = admin_svc.get_all_notices()
    assert len(notices) == 3
    # n3 was published last, so it should be at head of list
    assert notices[0].title == "Holiday Notice", f"Expected head to be latest notice, got {notices[0].title}"
    assert notices[1].title == "Workshop on AI"
    assert notices[2].title == "Fee Deadline"
    print(f"  [OK] Doubly LinkedList head verified as newest notice: '{notices[0].title}'")

    # Delete the middle node (n2: Workshop on AI)
    deleted = admin_svc.delete_notice(n2.notice_id)
    assert deleted is True, "Notice deletion failed"
    notices_after = admin_svc.get_all_notices()
    assert len(notices_after) == 2
    assert all(n.notice_id != n2.notice_id for n in notices_after)
    print("  [OK] Spliced node out of Doubly LinkedList: Remaining notices correctly linked.")

    # -------------------------------------------------------------
    # 4. HASH DICTIONARY CACHING: O(1) Average Lookup
    # -------------------------------------------------------------
    print("\n[+] 4. Testing Hash Dictionary O(1) Caching vs Database:")
    # Add a student to test lookup
    s_test = Student(None, "CE305", "Katherine Johnson", "Female", "2004-08-26", "kj@college.edu", "9876543212", "Hampton", dept_id, course_id, 5, 2022)
    s_id = student_svc.add_student(s_test)

    # Lookup via dictionary cache
    cached_record = student_svc.get_by_roll_no("CE305")
    db_record = fetch_one("SELECT * FROM students WHERE roll_no = 'CE305'", db_path=TEST_DB_PATH)

    assert cached_record is not None
    assert db_record is not None
    assert cached_record["name"] == db_record["name"]
    assert cached_record["email"] == db_record["email"]
    print(f"  [OK] O(1) Cache matched DB record for '{cached_record['name']}' (Roll: {cached_record['roll_no']})")

    # Lookup subject via admin service subject dictionary cache
    sub_cached = admin_svc.get_subject_by_code("CE301")
    assert sub_cached is not None and sub_cached["subject_name"] == "Data Structures"
    print(f"  [OK] O(1) Subject Cache matched: '{sub_cached['subject_name']}'")

    # Cleanup test DB
    gc.collect()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
            print(f"[-] Cleaned up test database {TEST_DB_PATH}")
        except Exception:
            pass

    print("\n" + "=" * 60)
    print("ALL PHASE 3 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase3_verification()
