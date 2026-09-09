"""
Security, Authentication, and Exception Handling utilities for College Management System.
Implements salted SHA-256 password hashing, user session management,
Role-Based Access Control (RBAC), and universal safe execution wrappers.
"""

import hashlib
import hmac
import os
import sqlite3
from typing import Any, Callable, Dict, Optional, Tuple

from database.database import fetch_one, DEFAULT_DB_PATH
from models.user import User, AdminUser, FacultyUser, StudentUser


def hash_password(plain_password: str, salt: Optional[str] = None) -> str:
    """
    Hash password using SHA-256 with a unique salt to prevent rainbow table attacks.
    Format: salt$hex_digest
    """
    if salt is None:
        salt = os.urandom(8).hex()  # 16-character hex salt
    key = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
    return f"{salt}${key}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify password against stored salt$hash string using constant-time comparison.
    """
    try:
        salt, expected_hash = stored_hash.split("$", 1)
        actual_hash = hashlib.sha256((salt + plain_password).encode("utf-8")).hexdigest()
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False


class UserSession:
    """
    Singleton managing active authenticated user session across the desktop application.
    """
    _instance: Optional["UserSession"] = None

    def __init__(self):
        self._current_user: Optional[User] = None

    @classmethod
    def get_instance(cls) -> "UserSession":
        if cls._instance is None:
            cls._instance = UserSession()
        return cls._instance

    def login(self, user: User) -> None:
        """Establish session for authenticated user."""
        self._current_user = user

    def logout(self) -> None:
        """Clear active user session."""
        self._current_user = None

    def get_current_user(self) -> Optional[User]:
        return self._current_user

    def is_authenticated(self) -> bool:
        return self._current_user is not None

    def has_role(self, role_name: str) -> bool:
        if not self._current_user:
            return False
        return self._current_user.role.lower() == role_name.lower()

    def get_role(self) -> str:
        if not self._current_user:
            return "Guest"
        return self._current_user.role


def authenticate_user(username: str, plain_password: str, db_path: Optional[str] = None) -> Tuple[bool, Optional[User], str]:
    """
    Authenticate user credentials against the SQLite users table.
    Returns: (success: bool, user_object: Optional[User], message: str)
    """
    clean_user = username.strip()
    if not clean_user:
        return False, None, "Username cannot be empty."
    if not plain_password:
        return False, None, "Password cannot be empty."

    query = "SELECT * FROM users WHERE username = ?;"
    user_row = fetch_one(query, (clean_user,), db_path=db_path)
    if not user_row:
        return False, None, "Invalid credentials. User does not exist."

    stored_hash = user_row["password_hash"]
    if not verify_password(plain_password, stored_hash):
        return False, None, "Invalid credentials. Incorrect password."

    role = user_row["role"]
    user_id = user_row["user_id"]

    # Instantiate role-specific OOP subclass (Polymorphism)
    if role == "Admin":
        user_obj: User = AdminUser(user_id=user_id, username=clean_user, password_hash=stored_hash)
    elif role == "Faculty":
        # Fetch associated faculty details if any
        fac = fetch_one("SELECT f.*, d.department_name FROM faculty f JOIN departments d ON f.department_id = d.department_id WHERE email LIKE ?", (f"%{clean_user}%",), db_path=db_path)
        fac_id = fac["faculty_id"] if fac else None
        dept = fac["department_name"] if fac else "Engineering"
        user_obj = FacultyUser(user_id=user_id, username=clean_user, faculty_id=fac_id, department=dept, password_hash=stored_hash)
    elif role == "Student":
        # Fetch associated student details if any
        stu = fetch_one("SELECT s.*, c.course_name FROM students s JOIN courses c ON s.course_id = c.course_id WHERE roll_no = ? OR email LIKE ?", (clean_user.upper(), f"%{clean_user}%"), db_path=db_path)
        s_id = stu["student_id"] if stu else None
        roll = stu["roll_no"] if stu else clean_user.upper()
        course = stu["course_name"] if stu else "B.E. Engineering"
        sem = stu["semester"] if stu else 1
        user_obj = StudentUser(user_id=user_id, username=clean_user, student_id=s_id, roll_no=roll, course_name=course, semester=sem, password_hash=stored_hash)
    else:
        return False, None, f"Unknown user role '{role}'."

    # Update global session
    UserSession.get_instance().login(user_obj)
    return True, user_obj, f"Login successful as {role}."


def safe_execute(action_name: str, func: Callable[..., Any], *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Universal Exception Handling Wrapper.
    Catches all DB errors, validation errors, file errors, and system exceptions,
    ensuring the application never crashes or outputs an unhandled stack trace.
    Returns: (success: bool, result: Any, error_message: Optional[str])
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except sqlite3.IntegrityError as e:
        err_msg = str(e)
        if "UNIQUE" in err_msg.upper():
            return False, None, f"Duplicate Record: A record with these unique details already exists in the system."
        elif "FOREIGN KEY" in err_msg.upper():
            return False, None, f"Relational Constraint: Cannot complete action because referenced foreign entity does not exist or is locked."
        elif "CHECK" in err_msg.upper():
            return False, None, f"Data Validation Error: Value violated database business constraint."
        return False, None, f"Database Integrity Error: {err_msg}"
    except sqlite3.OperationalError as e:
        return False, None, f"Database Connection Error: {str(e)}"
    except sqlite3.Error as e:
        return False, None, f"Database Error: {str(e)}"
    except ValueError as e:
        return False, None, f"Validation Error: {str(e)}"
    except FileNotFoundError as e:
        return False, None, f"File Not Found: The specified file '{e.filename}' could not be located."
    except KeyError as e:
        return False, None, f"Missing Parameter: Required field {str(e)} was not provided."
    except Exception as e:
        return False, None, f"Unexpected Error while {action_name}: {str(e)}"
