"""
Subject domain model demonstrating OOP Encapsulation and Data Integrity.
"""

from typing import Any, Dict, Optional


class Subject:
    """
    Subject domain model representing a college curriculum subject/module.
    """

    def __init__(
        self,
        subject_id: Optional[int],
        subject_code: str,
        subject_name: str,
        credits: int,
        semester: int,
        course_id: int,
        faculty_id: Optional[int] = None
    ):
        self._subject_id = subject_id
        self._subject_code = subject_code.strip().upper()
        self._subject_name = subject_name.strip()
        self._credits = credits
        self._semester = semester
        self._course_id = course_id
        self._faculty_id = faculty_id
        self._validate()

    def _validate(self) -> None:
        if not self._subject_code:
            raise ValueError("Subject code cannot be empty.")
        if not self._subject_name:
            raise ValueError("Subject name cannot be empty.")
        if not (1 <= self._credits <= 10):
            raise ValueError(f"Credits must be between 1 and 10 (got {self._credits}).")
        if not (1 <= self._semester <= 8):
            raise ValueError(f"Semester must be between 1 and 8 (got {self._semester}).")

    @property
    def subject_id(self) -> Optional[int]:
        return self._subject_id

    @subject_id.setter
    def subject_id(self, val: int):
        self._subject_id = val

    @property
    def subject_code(self) -> str:
        return self._subject_code

    @property
    def subject_name(self) -> str:
        return self._subject_name

    @subject_name.setter
    def subject_name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Subject name cannot be empty.")
        self._subject_name = val.strip()

    @property
    def credits(self) -> int:
        return self._credits

    @credits.setter
    def credits(self, val: int):
        if not (1 <= val <= 10):
            raise ValueError("Credits must be between 1 and 10.")
        self._credits = val

    @property
    def semester(self) -> int:
        return self._semester

    @property
    def course_id(self) -> int:
        return self._course_id

    @property
    def faculty_id(self) -> Optional[int]:
        return self._faculty_id

    @faculty_id.setter
    def faculty_id(self, val: Optional[int]):
        self._faculty_id = val

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_id": self._subject_id,
            "subject_code": self._subject_code,
            "subject_name": self._subject_name,
            "credits": self._credits,
            "semester": self._semester,
            "course_id": self._course_id,
            "faculty_id": self._faculty_id
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Subject":
        return cls(
            subject_id=row.get("subject_id"),
            subject_code=row.get("subject_code", ""),
            subject_name=row.get("subject_name", ""),
            credits=row.get("credits", 4),
            semester=row.get("semester", 1),
            course_id=row.get("course_id", 1),
            faculty_id=row.get("faculty_id")
        )

    def __repr__(self) -> str:
        return f"<Subject id={self._subject_id} code='{self._subject_code}' name='{self._subject_name}' credits={self._credits}>"
