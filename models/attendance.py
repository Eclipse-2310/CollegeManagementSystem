"""
Attendance domain model demonstrating OOP Encapsulation and Business Rule Validation.
"""

from typing import Any, Dict, Optional


class Attendance:
    """
    Attendance domain model representing a single student's attendance record for a subject on a date.
    """

    def __init__(
        self,
        attendance_id: Optional[int],
        student_id: int,
        subject_id: int,
        date: str,
        status: str
    ):
        self._attendance_id = attendance_id
        self._student_id = student_id
        self._subject_id = subject_id
        self._date = date.strip()
        self._status = status.strip()
        self._validate()

    def _validate(self) -> None:
        if self._status not in ("Present", "Absent"):
            raise ValueError(f"Attendance status must be 'Present' or 'Absent' (got '{self._status}').")
        if not self._date:
            raise ValueError("Attendance date cannot be empty.")

    @property
    def attendance_id(self) -> Optional[int]:
        return self._attendance_id

    @attendance_id.setter
    def attendance_id(self, val: int):
        self._attendance_id = val

    @property
    def student_id(self) -> int:
        return self._student_id

    @property
    def subject_id(self) -> int:
        return self._subject_id

    @property
    def date(self) -> str:
        return self._date

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, val: str):
        val_clean = val.strip()
        if val_clean not in ("Present", "Absent"):
            raise ValueError("Attendance status must be 'Present' or 'Absent'.")
        self._status = val_clean

    def is_present(self) -> bool:
        return self._status == "Present"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attendance_id": self._attendance_id,
            "student_id": self._student_id,
            "subject_id": self._subject_id,
            "date": self._date,
            "status": self._status
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Attendance":
        return cls(
            attendance_id=row.get("attendance_id"),
            student_id=row.get("student_id", 0),
            subject_id=row.get("subject_id", 0),
            date=row.get("date", ""),
            status=row.get("status", "Absent")
        )

    def __repr__(self) -> str:
        return f"<Attendance id={self._attendance_id} student={self._student_id} sub={self._subject_id} date={self._date} status={self._status}>"
