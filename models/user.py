"""
User Abstract Base Class (ABC) and role-specific subclasses demonstrating OOP
Inheritance, Encapsulation with properties, and Polymorphism via display_dashboard().
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class User(ABC):
    """
    Abstract Base Class for all system users.
    Demonstrates OOP Abstraction and Encapsulation.
    """

    def __init__(self, user_id: Optional[int], username: str, role: str, password_hash: str = ""):
        self._user_id = user_id
        self._username = username.strip()
        self._role = role
        self._password_hash = password_hash

    @property
    def user_id(self) -> Optional[int]:
        """Encapsulated getter for user_id."""
        return self._user_id

    @property
    def username(self) -> str:
        """Encapsulated getter for username."""
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or not value.strip():
            raise ValueError("Username cannot be empty.")
        self._username = value.strip()

    @property
    def role(self) -> str:
        """Encapsulated getter for role."""
        return self._role

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value: str):
        self._password_hash = value

    @abstractmethod
    def display_dashboard(self) -> Dict[str, Any]:
        """
        Abstract method demonstrating polymorphism.
        Each subclass must override and return a role-tailored dashboard structure.
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self._user_id,
            "username": self._username,
            "role": self._role
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._user_id} username='{self._username}' role='{self._role}'>"


class AdminUser(User):
    """
    Administrator role entity inheriting from User.
    Demonstrates Polymorphism via display_dashboard().
    """

    def __init__(self, user_id: Optional[int], username: str, password_hash: str = "", permissions: Optional[list] = None):
        super().__init__(user_id, username, "Admin", password_hash)
        self._permissions = permissions or [
            "manage_students", "manage_faculty", "manage_courses",
            "manage_departments", "manage_fees", "manage_library",
            "view_analytics", "manage_settings", "manage_timetable"
        ]

    @property
    def permissions(self) -> list:
        return list(self._permissions)

    def display_dashboard(self) -> Dict[str, Any]:
        """Polymorphic dashboard implementation for Admin role."""
        return {
            "role": "Admin",
            "title": f"Institutional Executive Dashboard — Welcome, {self.username}",
            "access_level": "Full System Master Control",
            "quick_actions": [
                "Student Enrollment & Records",
                "Faculty Allocation & Departments",
                "Fee Reconciliation & Dues",
                "Campus-wide Analytical Reports",
                "System Settings & User Privileges"
            ],
            "kpi_metrics_tracked": [
                "Total Enrolled Students",
                "Active Faculty Members",
                "Revenue & Pending Fees",
                "Campus Attendance Average",
                "Library Circulation Health"
            ]
        }


class FacultyUser(User):
    """
    Faculty role entity inheriting from User.
    Demonstrates Polymorphism via display_dashboard().
    """

    def __init__(self, user_id: Optional[int], username: str, faculty_id: Optional[int] = None,
                 department: str = "", password_hash: str = ""):
        super().__init__(user_id, username, "Faculty", password_hash)
        self._faculty_id = faculty_id
        self._department = department

    @property
    def faculty_id(self) -> Optional[int]:
        return self._faculty_id

    @property
    def department(self) -> str:
        return self._department

    def display_dashboard(self) -> Dict[str, Any]:
        """Polymorphic dashboard implementation for Faculty role."""
        return {
            "role": "Faculty",
            "title": f"Academic Faculty Portal — Welcome, Prof. {self.username}",
            "access_level": "Teaching & Academic Evaluation Control",
            "department": self._department or "Department Assigned",
            "quick_actions": [
                "Mark Daily Class Attendance",
                "Record Examination Marks",
                "View Subject Timetable",
                "Review Student Defaulter List (<75%)",
                "Post Course Announcements"
            ],
            "kpi_metrics_tracked": [
                "Allocated Subjects",
                "Scheduled Lectures Today",
                "Average Class Attendance %",
                "Pending Marks Submissions"
            ]
        }


class StudentUser(User):
    """
    Student role entity inheriting from User.
    Demonstrates Polymorphism via display_dashboard().
    """

    def __init__(self, user_id: Optional[int], username: str, student_id: Optional[int] = None,
                 roll_no: str = "", course_name: str = "", semester: int = 1, password_hash: str = ""):
        super().__init__(user_id, username, "Student", password_hash)
        self._student_id = student_id
        self._roll_no = roll_no
        self._course_name = course_name
        self._semester = semester

    @property
    def student_id(self) -> Optional[int]:
        return self._student_id

    @property
    def roll_no(self) -> str:
        return self._roll_no

    @property
    def course_name(self) -> str:
        return self._course_name

    @property
    def semester(self) -> int:
        return self._semester

    def display_dashboard(self) -> Dict[str, Any]:
        """Polymorphic dashboard implementation for Student role."""
        return {
            "role": "Student",
            "title": f"Student Academic Portal — Welcome, {self.username} (Roll: {self._roll_no})",
            "access_level": "Personal Academic & Account View",
            "course": f"{self._course_name} (Semester {self._semester})",
            "quick_actions": [
                "Check Personal Attendance Percentage",
                "View Semester Marks & Report Card",
                "Check Pending Fee Dues & Receipts",
                "Issued Library Books & Due Dates",
                "Campus Notices & Announcements"
            ],
            "kpi_metrics_tracked": [
                "My Overall Attendance %",
                "Current SGPA / Average %",
                "Outstanding Fee Balance",
                "Active Library Book Borrowings"
            ]
        }
