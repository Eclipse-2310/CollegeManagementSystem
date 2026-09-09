"""
Examination and Marks domain models demonstrating OOP Business Logic Encapsulation.
"""

from typing import Any, Dict, Optional, Tuple


class Examination:
    """
    Examination domain model representing an academic test or exam.
    """

    def __init__(
        self,
        exam_id: Optional[int],
        exam_name: str,
        subject_id: int,
        exam_date: str,
        total_marks: float
    ):
        self._exam_id = exam_id
        self._exam_name = exam_name.strip()
        self._subject_id = subject_id
        self._exam_date = exam_date.strip()
        self._total_marks = float(total_marks)
        self._validate()

    def _validate(self) -> None:
        if not self._exam_name:
            raise ValueError("Exam name cannot be empty.")
        if self._total_marks <= 0:
            raise ValueError(f"Total marks must be greater than 0 (got {self._total_marks}).")

    @property
    def exam_id(self) -> Optional[int]:
        return self._exam_id

    @exam_id.setter
    def exam_id(self, val: int):
        self._exam_id = val

    @property
    def exam_name(self) -> str:
        return self._exam_name

    @exam_name.setter
    def exam_name(self, val: str):
        if not val or not val.strip():
            raise ValueError("Exam name cannot be empty.")
        self._exam_name = val.strip()

    @property
    def subject_id(self) -> int:
        return self._subject_id

    @property
    def exam_date(self) -> str:
        return self._exam_date

    @property
    def total_marks(self) -> float:
        return self._total_marks

    @total_marks.setter
    def total_marks(self, val: float):
        val_f = float(val)
        if val_f <= 0:
            raise ValueError("Total marks must be greater than 0.")
        self._total_marks = val_f

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exam_id": self._exam_id,
            "exam_name": self._exam_name,
            "subject_id": self._subject_id,
            "exam_date": self._exam_date,
            "total_marks": self._total_marks
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Examination":
        return cls(
            exam_id=row.get("exam_id"),
            exam_name=row.get("exam_name", ""),
            subject_id=row.get("subject_id", 0),
            exam_date=row.get("exam_date", ""),
            total_marks=row.get("total_marks", 100.0)
        )

    def __repr__(self) -> str:
        return f"<Examination id={self._exam_id} name='{self._exam_name}' sub={self._subject_id} max={self._total_marks}>"


class Mark:
    """
    Mark domain model representing a student's score in an examination.
    Encapsulates percentage, letter grade, and grade points according to canonical thresholds.
    """

    def __init__(
        self,
        mark_id: Optional[int],
        student_id: int,
        exam_id: int,
        marks_obtained: float,
        total_marks: float = 100.0
    ):
        self._mark_id = mark_id
        self._student_id = student_id
        self._exam_id = exam_id
        self._marks_obtained = float(marks_obtained)
        self._total_marks = float(total_marks)
        self._validate()

    def _validate(self) -> None:
        if self._marks_obtained < 0:
            raise ValueError(f"Marks obtained cannot be negative (got {self._marks_obtained}).")
        if self._marks_obtained > self._total_marks:
            raise ValueError(f"Marks obtained ({self._marks_obtained}) cannot exceed total marks ({self._total_marks}).")

    @property
    def mark_id(self) -> Optional[int]:
        return self._mark_id

    @mark_id.setter
    def mark_id(self, val: int):
        self._mark_id = val

    @property
    def student_id(self) -> int:
        return self._student_id

    @property
    def exam_id(self) -> int:
        return self._exam_id

    @property
    def marks_obtained(self) -> float:
        return self._marks_obtained

    @marks_obtained.setter
    def marks_obtained(self, val: float):
        val_f = float(val)
        if val_f < 0:
            raise ValueError("Marks obtained cannot be negative.")
        if val_f > self._total_marks:
            raise ValueError(f"Marks obtained ({val_f}) cannot exceed total marks ({self._total_marks}).")
        self._marks_obtained = val_f

    @property
    def total_marks(self) -> float:
        return self._total_marks

    @property
    def percentage(self) -> float:
        if self._total_marks <= 0:
            return 0.0
        return round((self._marks_obtained / self._total_marks) * 100.0, 2)

    @staticmethod
    def calculate_grade(pct: float) -> Tuple[str, float, str]:
        """
        Returns (letter_grade, grade_point, remarks) according to canonical KI:
        >= 90: A+ (10.0, Outstanding)
        80-89.99: A (9.0, Excellent)
        70-79.99: B+ (8.0, Very Good)
        60-69.99: B (7.0, Good)
        50-59.99: C (6.0, Average)
        40-49.99: D (5.0, Marginal Pass)
        < 40: F (0.0, Fail)
        """
        if pct >= 90.0:
            return "A+", 10.0, "Outstanding"
        elif pct >= 80.0:
            return "A", 9.0, "Excellent"
        elif pct >= 70.0:
            return "B+", 8.0, "Very Good"
        elif pct >= 60.0:
            return "B", 7.0, "Good"
        elif pct >= 50.0:
            return "C", 6.0, "Average"
        elif pct >= 40.0:
            return "D", 5.0, "Marginal Pass"
        else:
            return "F", 0.0, "Fail"

    @property
    def grade(self) -> str:
        return self.calculate_grade(self.percentage)[0]

    @property
    def grade_point(self) -> float:
        return self.calculate_grade(self.percentage)[1]

    @property
    def is_passed(self) -> bool:
        return self.percentage >= 40.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mark_id": self._mark_id,
            "student_id": self._student_id,
            "exam_id": self._exam_id,
            "marks_obtained": self._marks_obtained,
            "total_marks": self._total_marks,
            "percentage": self.percentage,
            "grade": self.grade,
            "grade_point": self.grade_point,
            "is_passed": self.is_passed
        }

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Mark":
        return cls(
            mark_id=row.get("mark_id"),
            student_id=row.get("student_id", 0),
            exam_id=row.get("exam_id", 0),
            marks_obtained=row.get("marks_obtained", 0.0),
            total_marks=row.get("total_marks", 100.0)
        )

    def __repr__(self) -> str:
        return f"<Mark id={self._mark_id} student={self._student_id} score={self._marks_obtained}/{self._total_marks} grade={self.grade}>"
