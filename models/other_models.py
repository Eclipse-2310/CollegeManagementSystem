"""
Additional domain models: Fee, LibraryBook, LibraryTransaction, Notice, and TimetableSlot.
Demonstrates OOP modularity, encapsulation, and validation.
"""

from typing import Any, Dict, Optional


class FeeRecord:
    """
    FeeRecord domain model encapsulating college tuition fees, payments, and balances.
    Enforces pending_amount = total_fee - paid_amount.
    """

    def __init__(
        self,
        fee_id: Optional[int],
        student_id: int,
        total_fee: float,
        paid_amount: float = 0.0,
        pending_amount: Optional[float] = None,
        payment_date: Optional[str] = None,
        status: str = "Pending"
    ):
        self._fee_id = fee_id
        self._student_id = student_id
        self._total_fee = float(total_fee)
        self._paid_amount = float(paid_amount)
        self._pending_amount = float(pending_amount) if pending_amount is not None else (self._total_fee - self._paid_amount)
        self._payment_date = payment_date
        self._status = status.strip()
        self._validate()

    def _validate(self) -> None:
        if self._total_fee < 0:
            raise ValueError(f"Total fee cannot be negative (got {self._total_fee}).")
        if self._paid_amount < 0:
            raise ValueError(f"Paid amount cannot be negative (got {self._paid_amount}).")
        if self._paid_amount > self._total_fee:
            raise ValueError(f"Paid amount ({self._paid_amount}) cannot exceed total fee ({self._total_fee}).")
        # Ensure pending matches
        expected_pending = round(self._total_fee - self._paid_amount, 2)
        if round(self._pending_amount, 2) != expected_pending:
            self._pending_amount = expected_pending
        # Recalculate status
        if self._paid_amount >= self._total_fee:
            self._status = "Paid"
        elif self._paid_amount > 0:
            self._status = "Partial"
        else:
            self._status = "Pending"

    @property
    def fee_id(self) -> Optional[int]:
        return self._fee_id

    @fee_id.setter
    def fee_id(self, val: int):
        self._fee_id = val

    @property
    def student_id(self) -> int:
        return self._student_id

    @property
    def total_fee(self) -> float:
        return self._total_fee

    @property
    def paid_amount(self) -> float:
        return self._paid_amount

    @property
    def pending_amount(self) -> float:
        return self._pending_amount

    @property
    def payment_date(self) -> Optional[str]:
        return self._payment_date

    @property
    def status(self) -> str:
        return self._status

    def record_payment(self, amount: float, date_str: str) -> None:
        """Process an installment payment and re-evaluate balance and status."""
        amt = float(amount)
        if amt <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        if self._paid_amount + amt > self._total_fee:
            raise ValueError(f"Payment of {amt} exceeds outstanding pending balance of {self._pending_amount}.")
        self._paid_amount += amt
        self._pending_amount = self._total_fee - self._paid_amount
        self._payment_date = date_str
        self._validate()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fee_id": self._fee_id,
            "student_id": self._student_id,
            "total_fee": self._total_fee,
            "paid_amount": self._paid_amount,
            "pending_amount": self._pending_amount,
            "payment_date": self._payment_date,
            "status": self._status
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "FeeRecord":
        return cls(
            fee_id=row.get("fee_id"),
            student_id=row.get("student_id", 0),
            total_fee=row.get("total_fee", 0.0),
            paid_amount=row.get("paid_amount", 0.0),
            pending_amount=row.get("pending_amount"),
            payment_date=row.get("payment_date"),
            status=row.get("status", "Pending")
        )

    def __repr__(self) -> str:
        return f"<FeeRecord id={self._fee_id} student={self._student_id} total={self._total_fee} paid={self._paid_amount} pending={self._pending_amount}>"


class LibraryBook:
    """
    LibraryBook domain model representing a book in the college library catalog.
    """

    def __init__(
        self,
        book_id: Optional[int],
        title: str,
        author: str,
        category: str,
        isbn: str,
        quantity: int
    ):
        self._book_id = book_id
        self._title = title.strip()
        self._author = author.strip()
        self._category = category.strip()
        self._isbn = isbn.strip()
        self._quantity = int(quantity)
        self._validate()

    def _validate(self) -> None:
        if not self._title:
            raise ValueError("Book title cannot be empty.")
        if not self._author:
            raise ValueError("Author name cannot be empty.")
        if not self._isbn:
            raise ValueError("ISBN cannot be empty.")
        if self._quantity < 0:
            raise ValueError(f"Quantity cannot be negative (got {self._quantity}).")

    @property
    def book_id(self) -> Optional[int]:
        return self._book_id

    @book_id.setter
    def book_id(self, val: int):
        self._book_id = val

    @property
    def title(self) -> str:
        return self._title

    @property
    def author(self) -> str:
        return self._author

    @property
    def category(self) -> str:
        return self._category

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def quantity(self) -> int:
        return self._quantity

    @quantity.setter
    def quantity(self, val: int):
        if val < 0:
            raise ValueError("Quantity cannot be negative.")
        self._quantity = val

    def is_available(self) -> bool:
        return self._quantity > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "book_id": self._book_id,
            "title": self._title,
            "author": self._author,
            "category": self._category,
            "isbn": self._isbn,
            "quantity": self._quantity,
            "available": self.is_available()
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "LibraryBook":
        return cls(
            book_id=row.get("book_id"),
            title=row.get("title", ""),
            author=row.get("author", ""),
            category=row.get("category", ""),
            isbn=row.get("isbn", ""),
            quantity=row.get("quantity", 0)
        )

    def __repr__(self) -> str:
        return f"<LibraryBook id={self._book_id} title='{self._title}' qty={self._quantity}>"


class LibraryTransaction:
    """
    LibraryTransaction domain model representing an issue or return of a library book.
    """

    def __init__(
        self,
        transaction_id: Optional[int],
        book_id: int,
        student_id: int,
        issue_date: str,
        return_date: Optional[str] = None,
        status: str = "Issued"
    ):
        self._transaction_id = transaction_id
        self._book_id = book_id
        self._student_id = student_id
        self._issue_date = issue_date.strip()
        self._return_date = return_date.strip() if return_date else None
        self._status = status.strip()
        self._validate()

    def _validate(self) -> None:
        if self._status not in ("Issued", "Returned", "Overdue"):
            raise ValueError(f"Invalid transaction status '{self._status}'.")
        if not self._issue_date:
            raise ValueError("Issue date cannot be empty.")

    @property
    def transaction_id(self) -> Optional[int]:
        return self._transaction_id

    @property
    def book_id(self) -> int:
        return self._book_id

    @property
    def student_id(self) -> int:
        return self._student_id

    @property
    def issue_date(self) -> str:
        return self._issue_date

    @property
    def return_date(self) -> Optional[str]:
        return self._return_date

    @property
    def status(self) -> str:
        return self._status

    def mark_returned(self, return_date_str: str) -> None:
        self._return_date = return_date_str
        self._status = "Returned"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self._transaction_id,
            "book_id": self._book_id,
            "student_id": self._student_id,
            "issue_date": self._issue_date,
            "return_date": self._return_date,
            "status": self._status
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "LibraryTransaction":
        return cls(
            transaction_id=row.get("transaction_id"),
            book_id=row.get("book_id", 0),
            student_id=row.get("student_id", 0),
            issue_date=row.get("issue_date", ""),
            return_date=row.get("return_date"),
            status=row.get("status", "Issued")
        )

    def __repr__(self) -> str:
        return f"<LibraryTransaction id={self._transaction_id} book={self._book_id} student={self._student_id} status={self._status}>"


class Notice:
    """
    Notice domain model representing a campus notice or official announcement.
    """

    def __init__(
        self,
        notice_id: Optional[int],
        title: str,
        description: str,
        posted_by: str,
        posted_date: str
    ):
        self._notice_id = notice_id
        self._title = title.strip()
        self._description = description.strip()
        self._posted_by = posted_by.strip()
        self._posted_date = posted_date.strip()
        self._validate()

    def _validate(self) -> None:
        if not self._title:
            raise ValueError("Notice title cannot be empty.")
        if not self._description:
            raise ValueError("Notice description cannot be empty.")
        if not self._posted_by:
            raise ValueError("Posted by cannot be empty.")

    @property
    def notice_id(self) -> Optional[int]:
        return self._notice_id

    @notice_id.setter
    def notice_id(self, val: int):
        self._notice_id = val

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def posted_by(self) -> str:
        return self._posted_by

    @property
    def posted_date(self) -> str:
        return self._posted_date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "notice_id": self._notice_id,
            "title": self._title,
            "description": self._description,
            "posted_by": self._posted_by,
            "posted_date": self._posted_date
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Notice":
        return cls(
            notice_id=row.get("notice_id"),
            title=row.get("title", ""),
            description=row.get("description", ""),
            posted_by=row.get("posted_by", ""),
            posted_date=row.get("posted_date", "")
        )

    def __repr__(self) -> str:
        return f"<Notice id={self._notice_id} title='{self._title}' by='{self._posted_by}'>"


class TimetableSlot:
    """
    TimetableSlot domain model representing a scheduled lecture/lab.
    """

    VALID_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

    def __init__(
        self,
        timetable_id: Optional[int],
        subject_id: int,
        faculty_id: int,
        day: str,
        start_time: str,
        end_time: str,
        classroom: str
    ):
        self._timetable_id = timetable_id
        self._subject_id = subject_id
        self._faculty_id = faculty_id
        self._day = day.strip()
        self._start_time = start_time.strip()
        self._end_time = end_time.strip()
        self._classroom = classroom.strip()
        self._validate()

    def _validate(self) -> None:
        if self._day not in self.VALID_DAYS:
            raise ValueError(f"Invalid day '{self._day}'. Must be one of {self.VALID_DAYS}.")
        if not (self._start_time < self._end_time):
            raise ValueError(f"Start time ({self._start_time}) must be earlier than end time ({self._end_time}).")
        if not self._classroom:
            raise ValueError("Classroom cannot be empty.")

    @property
    def timetable_id(self) -> Optional[int]:
        return self._timetable_id

    @property
    def subject_id(self) -> int:
        return self._subject_id

    @property
    def faculty_id(self) -> int:
        return self._faculty_id

    @property
    def day(self) -> str:
        return self._day

    @property
    def start_time(self) -> str:
        return self._start_time

    @property
    def end_time(self) -> str:
        return self._end_time

    @property
    def classroom(self) -> str:
        return self._classroom

    def overlaps_with(self, other: "TimetableSlot") -> bool:
        """Check if this timetable slot overlaps with another slot on the same day."""
        if self._day != other._day:
            return False
        # Two time intervals [s1, e1) and [s2, e2) overlap if max(s1, s2) < min(e1, e2)
        return max(self._start_time, other._start_time) < min(self._end_time, other._end_time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timetable_id": self._timetable_id,
            "subject_id": self._subject_id,
            "faculty_id": self._faculty_id,
            "day": self._day,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "classroom": self._classroom
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "TimetableSlot":
        return cls(
            timetable_id=row.get("timetable_id"),
            subject_id=row.get("subject_id", 0),
            faculty_id=row.get("faculty_id", 0),
            day=row.get("day", "Monday"),
            start_time=row.get("start_time", "09:00"),
            end_time=row.get("end_time", "10:00"),
            classroom=row.get("classroom", "")
        )

    def __repr__(self) -> str:
        return f"<TimetableSlot id={self._timetable_id} day={self._day} {self._start_time}-{self._end_time} room={self._classroom}>"
