"""
Faculty domain model demonstrating OOP Encapsulation and Data Modeling.
"""

from typing import Any, Dict, Optional


class Faculty:
    """
    Encapsulates a faculty member with departmental and designation attributes.
    Demonstrates OOP Encapsulation with property decorators.
    """

    def __init__(
        self,
        faculty_id: Optional[int],
        name: str,
        email: str,
        phone: str,
        department_id: int,
        designation: str
    ):
        self._faculty_id = faculty_id
        self._name = name.strip()
        self._email = email.strip().lower()
        self._phone = phone.strip()
        self._department_id = department_id
        self._designation = designation.strip()
        self._validate()

    def _validate(self) -> None:
        if not self._name:
            raise ValueError("Faculty name cannot be empty.")
        if "@" not in self._email:
            raise ValueError(f"Invalid email: {self._email}")
        if not self._designation:
            raise ValueError("Designation cannot be empty.")

    @property
    def faculty_id(self) -> Optional[int]:
        return self._faculty_id

    @faculty_id.setter
    def faculty_id(self, val: int):
        self._faculty_id = val

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Name cannot be empty.")
        self._name = val.strip()

    @property
    def email(self) -> str:
        return self._email

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def department_id(self) -> int:
        return self._department_id

    @property
    def designation(self) -> str:
        return self._designation

    @designation.setter
    def designation(self, val: str):
        if not val or not val.strip():
            raise ValueError("Designation cannot be empty.")
        self._designation = val.strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "faculty_id": self._faculty_id,
            "name": self._name,
            "email": self._email,
            "phone": self._phone,
            "department_id": self._department_id,
            "designation": self._designation
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Faculty":
        return cls(
            faculty_id=row.get("faculty_id"),
            name=row.get("name", ""),
            email=row.get("email", ""),
            phone=row.get("phone", ""),
            department_id=row.get("department_id", 1),
            designation=row.get("designation", "")
        )

    def __repr__(self) -> str:
        return f"<Faculty id={self._faculty_id} name='{self._name}' desig='{self._designation}'>"
