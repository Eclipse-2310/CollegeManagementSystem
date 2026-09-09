"""
Attendance Service module for College Management System.
Handles daily class attendance recording, batch marking, percentage calculation,
and defaulter warning alerts based on canonical attendance thresholds.
"""

from typing import Any, Dict, List, Optional
import datetime

from database.database import (
    execute_query, fetch_all, fetch_one, get_attendance_percentage_report, DEFAULT_DB_PATH
)
from models.attendance import Attendance

# Canonical default threshold from Knowledge Item
DEFAULT_WARNING_THRESHOLD = 75.0


class AttendanceService:
    """
    Manages student attendance tracking, percentage calculations,
    and automatic defaulter warning alerts.
    """

    def __init__(self, db_path: Optional[str] = None, warning_threshold: float = DEFAULT_WARNING_THRESHOLD):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.warning_threshold = float(warning_threshold)

    def mark_attendance(self, student_id: int, subject_id: int, date: str, status: str) -> int:
        """
        Record or update attendance for a single student on a given date.
        Uses SQLite INSERT OR REPLACE based on UNIQUE(student_id, subject_id, date).
        """
        clean_status = status.strip()
        if clean_status not in ("Present", "Absent"):
            raise ValueError(f"Invalid attendance status '{clean_status}'. Must be 'Present' or 'Absent'.")

        query = """
            INSERT INTO attendance (student_id, subject_id, date, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, subject_id, date) DO UPDATE SET status = excluded.status;
        """
        return execute_query(query, (student_id, subject_id, date.strip(), clean_status), db_path=self.db_path)

    def mark_batch_attendance(self, subject_id: int, date: str, attendance_map: Dict[int, str]) -> int:
        """
        Batch record attendance for multiple students for a subject on a date.
        attendance_map: {student_id: 'Present' | 'Absent'}
        """
        records_saved = 0
        for s_id, status in attendance_map.items():
            self.mark_attendance(s_id, subject_id, date, status)
            records_saved += 1
        return records_saved

    def get_subject_attendance_summary(self, subject_id: int, student_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculates total classes, attended, missed, and percentage.
        Flags students below warning_threshold as defaulters.
        """
        raw_reports = get_attendance_percentage_report(subject_id=subject_id, student_id=student_id, db_path=self.db_path)
        enriched = []
        for r in raw_reports:
            item = dict(r)
            pct = item.get("attendance_percentage", 0.0)
            item["is_defaulter"] = pct < self.warning_threshold
            item["threshold"] = self.warning_threshold
            item["status_label"] = "Shortage (Defaulter)" if item["is_defaulter"] else "Satisfactory"
            enriched.append(item)
        return enriched

    def get_student_overall_attendance(self, student_id: int) -> Dict[str, Any]:
        """
        Calculates aggregate campus attendance for a specific student across all subjects.
        Edge case: If student has 0 classes scheduled, returns 100.0% with note.
        """
        query = """
            SELECT 
                COUNT(*) AS total_classes,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS attended_classes,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) AS missed_classes
            FROM attendance
            WHERE student_id = ?;
        """
        res = fetch_one(query, (student_id,), db_path=self.db_path)
        if not res or res["total_classes"] == 0:
            return {
                "student_id": student_id,
                "total_classes": 0,
                "attended_classes": 0,
                "missed_classes": 0,
                "percentage": 100.0,
                "is_defaulter": False,
                "warning_threshold": self.warning_threshold,
                "note": "No classes scheduled yet."
            }

        total = res["total_classes"]
        attended = res["attended_classes"] or 0
        missed = res["missed_classes"] or 0
        pct = round((attended / total) * 100.0, 2)
        is_defaulter = pct < self.warning_threshold

        return {
            "student_id": student_id,
            "total_classes": total,
            "attended_classes": attended,
            "missed_classes": missed,
            "percentage": pct,
            "is_defaulter": is_defaulter,
            "warning_threshold": self.warning_threshold,
            "note": "Defaulter Warning Issued" if is_defaulter else "Attendance in Good Standing"
        }

    def get_defaulters_list(self, subject_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Returns all students whose attendance is below the configured threshold (< 75%).
        Used for warning notices, parental SMS notifications, and exam clearance.
        """
        all_records = self.get_subject_attendance_summary(subject_id=subject_id)
        return [r for r in all_records if r["is_defaulter"]]
