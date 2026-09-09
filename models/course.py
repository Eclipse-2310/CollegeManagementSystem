"""
Department and Course domain models demonstrating OOP Composition and Encapsulation.
"""

from typing import Any, Dict, Optional


class Department:
    """
    Department domain model representing an academic department.
    """

    def __init__(self, department_id: Optional[int], department_name: str, department_code: str):
        self._department_id = department_id
        self._department_name = department_name.strip()
        self._department_code = department_code.strip().upper()
        self._validate()

    def _validate(self) -> None:
        if not self._department_name:
            raise ValueError("Department name cannot be empty.")
        if not self._department_code:
            raise ValueError("Department code cannot be empty.")

    @property
    def department_id(self) -> Optional[int]:
        return self._department_id

    @department_id.setter
    def department_id(self, val: int):
        self._department_id = val

    @property
    def department_name(self) -> str:
        return self._department_name

    @department_name.setter
    def department_name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Department name cannot be empty.")
        self._department_name = val.strip()

    @property
    def department_code(self) -> str:
        return self._department_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "department_id": self._department_id,
            "department_name": self._department_name,
            "department_code": self._department_code
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Department":
        return cls(
            department_id=row.get("department_id"),
            department_name=row.get("department_name", ""),
            department_code=row.get("department_code", "")
        )

    def __repr__(self) -> str:
        return f"<Department id={self._department_id} code='{self._department_code}' name='{self._department_name}'>"


class Course:
    """
    Course domain model representing an academic degree program.
    """

    def __init__(
        self,
        course_id: Optional[int],
        course_name: str,
        course_code: str,
        department_id: int,
        duration: int
    ):
        self._course_id = course_id
        self._course_name = course_name.strip()
        self._course_code = course_code.strip().upper()
        self._department_id = department_id
        self._duration = duration
        self._validate()

    def _validate(self) -> None:
        if not self._course_name:
            raise ValueError("Course name cannot be empty.")
        if not self._course_code:
            raise ValueError("Course code cannot be empty.")
        if self._duration <= 0:
            raise ValueError(f"Duration must be a positive integer in years (got {self._duration}).")

    @property
    def course_id(self) -> Optional[int]:
        return self._course_id

    @course_id.setter
    def course_id(self, val: int):
        self._course_id = val

    @property
    def course_name(self) -> str:
        return self._course_name

    @course_name.setter
    def course_name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Course name cannot be empty.")
        self._course_name = val.strip()

    @property
    def course_code(self) -> str:
        return self._course_code

    @property
    def department_id(self) -> int:
        return self._department_id

    @property
    def duration(self) -> int:
        return self._duration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "course_id": self._course_id,
            "course_name": self._course_name,
            "course_code": self._course_code,
            "department_id": self._department_id,
            "duration": self._duration
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Course":
        return cls(
            course_id=row.get("course_id"),
            course_name=row.get("course_name", ""),
            course_code=row.get("course_code", ""),
            department_id=row.get("department_id", 1),
            duration=row.get("duration", 4)
        )

    def __repr__(self) -> str:
        return f"<Course id={self._course_id} code='{self._course_code}' name='{self._course_name}'>"
