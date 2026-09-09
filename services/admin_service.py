"""
Admin Service module for College Management System.
Manages Departments, Courses, Subjects, Timetable Conflict Detection,
and integrates custom Doubly LinkedList for the Campus Notice Board.
"""

from typing import Any, Dict, List, Optional, Tuple
import datetime

from database.database import (
    execute_query, fetch_all, fetch_one, DEFAULT_DB_PATH
)
from models.course import Department, Course
from models.subject import Subject
from models.other_models import Notice, TimetableSlot
from data_structures.linked_list import DoublyLinkedList


class AdminService:
    """
    Manages institutional configuration, timetable conflict checking,
    and notice board chain.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

        # DATA STRUCTURE 3: Doubly LinkedList for Chronological Notice Board
        # Inserting at front (O(1)) puts latest announcements at the top
        self.notice_chain: DoublyLinkedList[Notice] = DoublyLinkedList[Notice]()
        self.refresh_notices_from_db()

        # In-memory dictionary cache for Subject by Code (O(1) average lookup)
        self._subject_cache: Dict[str, Dict[str, Any]] = {}
        self.refresh_subject_cache()

    def refresh_subject_cache(self) -> None:
        """Cache subjects by subject_code for O(1) fast lookup."""
        self._subject_cache.clear()
        try:
            subjects = fetch_all("SELECT * FROM subjects;", db_path=self.db_path)
            for sub in subjects:
                self._subject_cache[sub["subject_code"].upper()] = sub
        except Exception:
            pass

    def get_subject_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Average-case O(1) dictionary lookup."""
        clean_code = code.strip().upper()
        if clean_code in self._subject_cache:
            return self._subject_cache[clean_code]
        res = fetch_one("SELECT * FROM subjects WHERE subject_code = ?", (clean_code,), db_path=self.db_path)
        if res:
            self._subject_cache[clean_code] = res
        return res

    def refresh_notices_from_db(self) -> None:
        """Load notices from DB into the Doubly LinkedList chain."""
        self.notice_chain.clear()
        try:
            rows = fetch_all("SELECT * FROM notices ORDER BY posted_date ASC, notice_id ASC;", db_path=self.db_path)
            for r in rows:
                notice = Notice.from_row(r)
                # insert_front so latest appears at head of linked list
                self.notice_chain.insert_front(notice)
        except Exception:
            pass

    def publish_notice(self, title: str, description: str, posted_by: str, date_str: Optional[str] = None) -> Notice:
        """
        Publish a notice, persist to database, and insert_front into Doubly LinkedList.
        Demonstrates O(1) front insertion on linked node structure.
        """
        p_date = date_str or datetime.date.today().isoformat()
        query = "INSERT INTO notices (title, description, posted_by, posted_date) VALUES (?, ?, ?, ?);"
        n_id = execute_query(query, (title, description, posted_by, p_date), db_path=self.db_path)

        new_notice = Notice(n_id, title, description, posted_by, p_date)
        # O(1) prepend into LinkedList
        self.notice_chain.insert_front(new_notice)
        return new_notice

    def delete_notice(self, notice_id: int) -> bool:
        """
        Delete notice from DB and unlink from the Doubly LinkedList.
        Demonstrates O(n) search + O(1) pointer reconnection.
        """
        execute_query("DELETE FROM notices WHERE notice_id = ?", (notice_id,), db_path=self.db_path)
        return self.notice_chain.delete(lambda n: n.notice_id == notice_id)

    def get_all_notices(self) -> List[Notice]:
        """Return notices from LinkedList head to tail."""
        return self.notice_chain.to_list()

    # ==========================================
    # Timetable & Double-Booking Conflict Detection
    # ==========================================

    def check_timetable_conflict(
        self,
        day: str,
        start_time: str,
        end_time: str,
        faculty_id: int,
        classroom: str,
        exclude_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Business Rule: Double-Booking Conflict Prevention.
        Rejects a timetable slot if:
        1. Same faculty has another class at an overlapping time on the same day.
        2. Same classroom is already booked for another class at an overlapping time on the same day.
        Returns: (has_conflict, conflict_reason)
        """
        query = """
            SELECT t.*, s.subject_name, f.name AS faculty_name 
            FROM timetable t
            JOIN subjects s ON t.subject_id = s.subject_id
            JOIN faculty f ON t.faculty_id = f.faculty_id
            WHERE t.day = ?
        """
        params = [day]
        if exclude_id:
            query += " AND t.timetable_id != ?"
            params.append(exclude_id)

        existing_slots = fetch_all(query, tuple(params), db_path=self.db_path)

        for slot in existing_slots:
            s_start = slot["start_time"]
            s_end = slot["end_time"]

            # Check time interval overlap: max(start1, start2) < min(end1, end2)
            if max(start_time, s_start) < min(end_time, s_end):
                if slot["faculty_id"] == faculty_id:
                    return True, (
                        f"Faculty Conflict: {slot['faculty_name']} is already scheduled for "
                        f"'{slot['subject_name']}' from {s_start} to {s_end} in {slot['classroom']}."
                    )
                if slot["classroom"].strip().upper() == classroom.strip().upper():
                    return True, (
                        f"Classroom Conflict: Room {classroom} is already occupied by "
                        f"{slot['faculty_name']} for '{slot['subject_name']}' from {s_start} to {s_end}."
                    )

        return False, None

    def add_timetable_slot(self, slot: TimetableSlot) -> int:
        """
        Add a timetable slot after validating for conflicts.
        """
        has_conflict, reason = self.check_timetable_conflict(
            day=slot.day,
            start_time=slot.start_time,
            end_time=slot.end_time,
            faculty_id=slot.faculty_id,
            classroom=slot.classroom
        )
        if has_conflict:
            raise ValueError(f"Timetable Double-Booking: {reason}")

        query = """
            INSERT INTO timetable (subject_id, faculty_id, day, start_time, end_time, classroom)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (slot.subject_id, slot.faculty_id, slot.day, slot.start_time, slot.end_time, slot.classroom)
        return execute_query(query, params, db_path=self.db_path)
