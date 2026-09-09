"""
Validation routines for College Management System.
Returns clean, user-friendly error messages rather than unhandled tracebacks.
"""

import re
import datetime
from typing import Any, Dict, List, Optional, Tuple

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^[6-9]\d{9}$")  # Standard 10-digit mobile number


def validate_required(value: Any, field_name: str) -> Tuple[bool, Optional[str]]:
    """Validate that a field is non-empty."""
    if value is None:
        return False, f"'{field_name}' is required."
    val_str = str(value).strip()
    if not val_str:
        return False, f"'{field_name}' cannot be left blank."
    return True, None


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email format."""
    ok, err = validate_required(email, "Email")
    if not ok:
        return False, err
    if not EMAIL_REGEX.match(email.strip()):
        return False, f"'{email}' is not a valid email address (e.g. student@college.edu)."
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate 10-digit phone number format."""
    ok, err = validate_required(phone, "Phone Number")
    if not ok:
        return False, err
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    if not PHONE_REGEX.match(clean_phone):
        return False, f"'{phone}' must be a valid 10-digit mobile number starting with 6-9."
    return True, None


def validate_roll_no(roll_no: str) -> Tuple[bool, Optional[str]]:
    """Validate roll number format (alphanumeric, 3 to 15 chars)."""
    ok, err = validate_required(roll_no, "Roll Number")
    if not ok:
        return False, err
    clean_roll = roll_no.strip()
    if len(clean_roll) < 3 or len(clean_roll) > 15:
        return False, "Roll number must be between 3 and 15 alphanumeric characters."
    return True, None


def validate_date(date_str: str, field_name: str = "Date") -> Tuple[bool, Optional[str]]:
    """Validate date in YYYY-MM-DD format."""
    ok, err = validate_required(date_str, field_name)
    if not ok:
        return False, err
    try:
        datetime.date.fromisoformat(date_str.strip())
        return True, None
    except ValueError:
        return False, f"{field_name} must be a valid calendar date in YYYY-MM-DD format (got '{date_str}')."


def validate_semester(semester: Any) -> Tuple[bool, Optional[str]]:
    """Validate semester range (1 to 8)."""
    try:
        sem_int = int(semester)
        if 1 <= sem_int <= 8:
            return True, None
        return False, f"Semester must be between 1 and 8 (got {semester})."
    except (ValueError, TypeError):
        return False, "Semester must be a valid integer between 1 and 8."


def validate_marks(marks_obtained: Any, total_marks: Any) -> Tuple[bool, Optional[str]]:
    """Validate marks are numeric, non-negative, and not exceeding maximum."""
    try:
        obtained = float(marks_obtained)
        maximum = float(total_marks)
    except (ValueError, TypeError):
        return False, "Marks must be valid numbers."

    if obtained < 0:
        return False, f"Marks obtained cannot be negative (got {obtained})."
    if maximum <= 0:
        return False, f"Maximum marks must be greater than zero (got {maximum})."
    if obtained > maximum:
        return False, f"Marks obtained ({obtained}) cannot exceed maximum exam marks ({maximum})."
    return True, None


def validate_fee_amounts(total_fee: Any, paid_amount: Any) -> Tuple[bool, Optional[str]]:
    """Validate fee amounts are non-negative and paid does not exceed total."""
    try:
        total = float(total_fee)
        paid = float(paid_amount)
    except (ValueError, TypeError):
        return False, "Fee amounts must be valid numbers."

    if total < 0:
        return False, f"Total fee cannot be negative (got {total})."
    if paid < 0:
        return False, f"Paid amount cannot be negative (got {paid})."
    if paid > total:
        return False, f"Paid amount (₹{paid:,.2f}) cannot exceed total fee (₹{total:,.2f})."
    return True, None


def validate_attendance_status(status: str) -> Tuple[bool, Optional[str]]:
    """Validate attendance status."""
    clean = str(status).strip()
    if clean in ("Present", "Absent"):
        return True, None
    return False, f"Attendance status must be 'Present' or 'Absent' (got '{status}')."


def validate_student_form(data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
    """
    Validates complete student form dictionary.
    Returns (is_valid, errors_dict).
    """
    errors: Dict[str, str] = {}

    ok, err = validate_roll_no(data.get("roll_no", ""))
    if not ok and err:
        errors["roll_no"] = err

    ok, err = validate_required(data.get("name", ""), "Student Name")
    if not ok and err:
        errors["name"] = err

    ok, err = validate_email(data.get("email", ""))
    if not ok and err:
        errors["email"] = err

    ok, err = validate_phone(data.get("phone", ""))
    if not ok and err:
        errors["phone"] = err

    ok, err = validate_date(data.get("date_of_birth", ""), "Date of Birth")
    if not ok and err:
        errors["date_of_birth"] = err

    ok, err = validate_semester(data.get("semester", 1))
    if not ok and err:
        errors["semester"] = err

    gender = str(data.get("gender", "")).strip()
    if gender not in ("Male", "Female", "Other"):
        errors["gender"] = "Gender must be Male, Female, or Other."

    return len(errors) == 0, errors
