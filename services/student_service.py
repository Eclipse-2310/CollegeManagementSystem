"""
Student Service module for College Management System.
Integrates Database persistence with custom Stack (Undo Action History)
and Hash Dictionaries for O(1) in-memory fast lookups.
"""

from typing import Any, Dict, List, Optional
import sqlite3

from database.database import (
    execute_query, fetch_all, fetch_one, get_students_with_details, DEFAULT_DB_PATH
)
from models.student import Student
from data_structures.stack import Stack, ActionRecord


class StudentService:
    """
    Manages student lifecycle, registration, updates, deletions,
    and fast in-memory caching with undo history tracking.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

        # DATA STRUCTURE 1: Stack for Action History & Undo Operations (LIFO)
        self.undo_stack: Stack[ActionRecord] = Stack[ActionRecord](max_size=50)

        # DATA STRUCTURE 4: In-Memory Hash Dictionary Cache
        # Provides Average-case O(1) lookup by roll number, avoiding O(n) table scans
        self._roll_no_cache: Dict[str, Dict[str, Any]] = {}
        self.refresh_cache()

    def refresh_cache(self) -> None:
        """
        Populate the in-memory hash dictionary cache from the database.
        Hash table access:
            - Average Case: O(1)
            - Worst Case: O(n) during hash collisions
        """
        self._roll_no_cache.clear()
        try:
            students = get_students_with_details(db_path=self.db_path)
            for s in students:
                self._roll_no_cache[s["roll_no"].upper()] = s
        except Exception:
            pass

    def get_by_roll_no(self, roll_no: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve student details by roll number in O(1) time via hash dictionary.
        Falls back to database query if not present in cache.
        """
        clean_roll = roll_no.strip().upper()
        # Fast path: O(1) dictionary lookup
        if clean_roll in self._roll_no_cache:
            return self._roll_no_cache[clean_roll]

        # Fallback path: database parameterized query
        query = """
            SELECT s.*, d.department_name, c.course_name 
            FROM students s
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.roll_no = ?
        """
        res = fetch_one(query, (clean_roll,), db_path=self.db_path)
        if res:
            self._roll_no_cache[clean_roll] = res
        return res

    def get_all_students(self, department_id: Optional[int] = None, course_id: Optional[int] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve student records with department and course information."""
        return get_students_with_details(department_id=department_id, course_id=course_id, search_text=search, db_path=self.db_path)

    def add_student(self, student: Student, track_undo: bool = True) -> int:
        """
        Register a new student, update the O(1) cache, and push to Undo Stack.
        """
        query = """
            INSERT INTO students 
            (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        params = (
            student.roll_no,
            student.name,
            student.gender,
            student.date_of_birth,
            student.email,
            student.phone,
            student.address,
            student.department_id,
            student.course_id,
            student.semester,
            student.admission_year
        )
        new_id = execute_query(query, params, db_path=self.db_path)
        student.student_id = new_id

        # Update cache in O(1)
        self.refresh_cache()

        # Push to Undo Stack (LIFO)
        if track_undo:
            def rollback():
                self.delete_student(new_id, track_undo=False)

            action = ActionRecord(
                action_type="ADD_STUDENT",
                description=f"Added student {student.name} ({student.roll_no})",
                entity_type="Student",
                entity_id=new_id,
                rollback_fn=rollback,
                payload=student.to_dict()
            )
            self.undo_stack.push(action)

        return new_id

    def update_student(self, student_id: int, updated_data: Dict[str, Any], track_undo: bool = True) -> bool:
        """
        Update an existing student's record and record previous state in Undo Stack.
        """
        # Fetch previous state for undo capability
        old_data = fetch_one("SELECT * FROM students WHERE student_id = ?", (student_id,), db_path=self.db_path)
        if not old_data:
            raise ValueError(f"Student #{student_id} not found.")

        query = """
            UPDATE students SET
                roll_no = ?, name = ?, gender = ?, date_of_birth = ?,
                email = ?, phone = ?, address = ?, department_id = ?,
                course_id = ?, semester = ?, admission_year = ?
            WHERE student_id = ?;
        """
        params = (
            updated_data.get("roll_no", old_data["roll_no"]),
            updated_data.get("name", old_data["name"]),
            updated_data.get("gender", old_data["gender"]),
            updated_data.get("date_of_birth", old_data["date_of_birth"]),
            updated_data.get("email", old_data["email"]),
            updated_data.get("phone", old_data["phone"]),
            updated_data.get("address", old_data["address"]),
            updated_data.get("department_id", old_data["department_id"]),
            updated_data.get("course_id", old_data["course_id"]),
            updated_data.get("semester", old_data["semester"]),
            updated_data.get("admission_year", old_data["admission_year"]),
            student_id
        )
        execute_query(query, params, db_path=self.db_path)
        self.refresh_cache()

        if track_undo:
            def rollback():
                self.update_student(student_id, old_data, track_undo=False)

            action = ActionRecord(
                action_type="UPDATE_STUDENT",
                description=f"Updated details for student #{student_id}",
                entity_type="Student",
                entity_id=student_id,
                rollback_fn=rollback,
                payload=old_data
            )
            self.undo_stack.push(action)

        return True

    def delete_student(self, student_id: int, track_undo: bool = True) -> bool:
        """
        Delete student with cascade cleanup and push to Undo Stack for restoration.
        """
        old_data = fetch_one("SELECT * FROM students WHERE student_id = ?", (student_id,), db_path=self.db_path)
        if not old_data:
            return False

        execute_query("DELETE FROM students WHERE student_id = ?", (student_id,), db_path=self.db_path)
        self.refresh_cache()

        if track_undo:
            def rollback():
                # Re-insert original record
                restored_student = Student(
                    student_id=old_data["student_id"],
                    roll_no=old_data["roll_no"],
                    name=old_data["name"],
                    gender=old_data["gender"],
                    date_of_birth=old_data["date_of_birth"],
                    email=old_data["email"],
                    phone=old_data["phone"],
                    address=old_data["address"],
                    department_id=old_data["department_id"],
                    course_id=old_data["course_id"],
                    semester=old_data["semester"],
                    admission_year=old_data["admission_year"]
                )
                self.add_student(restored_student, track_undo=False)

            action = ActionRecord(
                action_type="DELETE_STUDENT",
                description=f"Deleted student {old_data['name']} ({old_data['roll_no']})",
                entity_type="Student",
                entity_id=student_id,
                rollback_fn=rollback,
                payload=old_data
            )
            self.undo_stack.push(action)

        return True

    def undo_last_action(self) -> Optional[str]:
        """
        Pops the most recent action from the LIFO Stack and executes its rollback function.
        Returns a human-readable confirmation message or None if stack is empty.
        """
        if self.undo_stack.is_empty():
            return None
        action = self.undo_stack.pop()
        action.undo()
        self.refresh_cache()
        return f"Undid action: {action.description}"
