"""
Student domain model demonstrating OOP Encapsulation and Data Validation.
"""

from typing import Any, Dict, Optional
import datetime


class Student:
    """
    Encapsulates a student entity with validated properties.
    Demonstrates OOP Encapsulation with protected member variables and getters/setters.
    """

    def __init__(
        self,
        student_id: Optional[int],
        roll_no: str,
        name: str,
        gender: str,
        date_of_birth: str,
        email: str,
        phone: str,
        address: str,
        department_id: int,
        course_id: int,
        semester: int,
        admission_year: int
    ):
        self._student_id = student_id
        self._roll_no = roll_no.strip().upper()
        self._name = name.strip()
        self._gender = gender.strip()
        self._date_of_birth = date_of_birth.strip()
        self._email = email.strip().lower()
        self._phone = phone.strip()
        self._address = address.strip()
        self._department_id = department_id
        self._course_id = course_id
        self._semester = semester
        self._admission_year = admission_year

        # Run validation
        self._validate()

    def _validate(self) -> None:
        """Internal validation enforcing schema business rules."""
        if not self._roll_no:
            raise ValueError("Roll number cannot be empty.")
        if not self._name:
            raise ValueError("Student name cannot be empty.")
        if self._gender not in ("Male", "Female", "Other"):
            raise ValueError(f"Invalid gender '{self._gender}'. Must be Male, Female, or Other.")
        if not (1 <= self._semester <= 8):
            raise ValueError(f"Semester must be between 1 and 8 (got {self._semester}).")
        if self._admission_year < 2000:
            raise ValueError(f"Admission year must be 2000 or later (got {self._admission_year}).")

    @property
    def student_id(self) -> Optional[int]:
        return self._student_id

    @student_id.setter
    def student_id(self, val: int):
        self._student_id = val

    @property
    def roll_no(self) -> str:
        return self._roll_no

    @roll_no.setter
    def roll_no(self, val: str):
        if not val or not val.strip():
            raise ValueError("Roll number cannot be empty.")
        self._roll_no = val.strip().upper()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Name cannot be empty.")
        self._name = val.strip()

    @property
    def gender(self) -> str:
        return self._gender

    @property
    def date_of_birth(self) -> str:
        return self._date_of_birth

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, val: str):
        if "@" not in val or "." not in val:
            raise ValueError(f"Invalid email format: {val}")
        self._email = val.strip().lower()

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def address(self) -> str:
        return self._address

    @property
    def department_id(self) -> int:
        return self._department_id

    @property
    def course_id(self) -> int:
        return self._course_id

    @property
    def semester(self) -> int:
        return self._semester

    @semester.setter
    def semester(self, val: int):
        if not (1 <= val <= 8):
            raise ValueError(f"Semester must be between 1 and 8 (got {val}).")
        self._semester = val

    @property
    def admission_year(self) -> int:
        return self._admission_year

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self._student_id,
            "roll_no": self._roll_no,
            "name": self._name,
            "gender": self._gender,
            "date_of_birth": self._date_of_birth,
            "email": self._email,
            "phone": self._phone,
            "address": self._address,
            "department_id": self._department_id,
            "course_id": self._course_id,
            "semester": self._semester,
            "admission_year": self._admission_year
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Student":
        return cls(
            student_id=row.get("student_id"),
            roll_no=row.get("roll_no", ""),
            name=row.get("name", ""),
            gender=row.get("gender", "Male"),
            date_of_birth=row.get("date_of_birth", ""),
            email=row.get("email", ""),
            phone=row.get("phone", ""),
            address=row.get("address", ""),
            department_id=row.get("department_id", 1),
            course_id=row.get("course_id", 1),
            semester=row.get("semester", 1),
            admission_year=row.get("admission_year", 2024)
        )

    def __repr__(self) -> str:
        return f"<Student id={self._student_id} roll='{self._roll_no}' name='{self._name}' sem={self._semester}>"
