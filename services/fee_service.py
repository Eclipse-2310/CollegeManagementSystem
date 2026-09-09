"""
Fee Management Service module for College Management System.
Enforces financial invariants (pending_amount = total_fee - paid_amount),
rejects negative fees or overpayments, and tracks fee dues and receipts.
"""

from typing import Any, Dict, List, Optional
import datetime

from database.database import (
    execute_query, fetch_all, fetch_one, get_fee_collection_summary, DEFAULT_DB_PATH
)
from models.other_models import FeeRecord


class FeeService:
    """
    Manages student fee ledgers, payment transactions, receipt generation,
    and outstanding dues reconciliation.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

    def create_fee_record(self, student_id: int, total_fee: float, paid_amount: float = 0.0) -> int:
        """
        Create a new student fee invoice.
        Rejects negative amounts.
        """
        fee = FeeRecord(None, student_id, total_fee, paid_amount)
        query = """
            INSERT INTO fees (student_id, total_fee, paid_amount, pending_amount, payment_date, status)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        params = (
            fee.student_id,
            fee.total_fee,
            fee.paid_amount,
            fee.pending_amount,
            fee.payment_date,
            fee.status
        )
        return execute_query(query, params, db_path=self.db_path)

    def record_payment(self, fee_id: int, amount: float, payment_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Record a payment against an existing fee invoice.
        Business Rules Enforced:
        1. Amount cannot be negative or zero.
        2. Amount cannot exceed outstanding pending balance.
        3. Pending amount is strictly recalculated as total_fee - paid_amount.
        4. Status updated to 'Paid', 'Partial', or 'Pending'.
        """
        record = fetch_one("SELECT * FROM fees WHERE fee_id = ?", (fee_id,), db_path=self.db_path)
        if not record:
            raise ValueError(f"Fee record #{fee_id} not found.")

        payment_amt = float(amount)
        if payment_amt <= 0:
            raise ValueError(f"Payment amount must be positive (got {payment_amt}).")

        fee = FeeRecord.from_row(record)
        if payment_amt > fee.pending_amount:
            raise ValueError(
                f"Payment amount (₹{payment_amt:.2f}) exceeds outstanding pending balance (₹{fee.pending_amount:.2f})."
            )

        date_str = payment_date or datetime.date.today().isoformat()
        fee.record_payment(payment_amt, date_str)

        update_query = """
            UPDATE fees SET
                paid_amount = ?,
                pending_amount = ?,
                payment_date = ?,
                status = ?
            WHERE fee_id = ?;
        """
        execute_query(
            update_query,
            (fee.paid_amount, fee.pending_amount, fee.payment_date, fee.status, fee_id),
            db_path=self.db_path
        )

        return fee.to_dict()

    def get_student_fee_details(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve fee record for a specific student."""
        query = """
            SELECT f.*, s.name AS student_name, s.roll_no, d.department_name, c.course_name
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            JOIN departments d ON s.department_id = d.department_id
            JOIN courses c ON s.course_id = c.course_id
            WHERE f.student_id = ?;
        """
        return fetch_one(query, (student_id,), db_path=self.db_path)

    def get_all_fees(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all fee records with optional status filter ('Paid', 'Partial', 'Pending')."""
        query = """
            SELECT f.*, s.name AS student_name, s.roll_no, d.department_name
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            JOIN departments d ON s.department_id = d.department_id
            WHERE 1=1
        """
        params = []
        if status:
            query += " AND f.status = ?"
            params.append(status)
        query += " ORDER BY f.pending_amount DESC;"
        return fetch_all(query, tuple(params), db_path=self.db_path)

    def get_fee_defaulters(self) -> List[Dict[str, Any]]:
        """Return all students who have an outstanding pending fee balance."""
        query = """
            SELECT f.*, s.name AS student_name, s.roll_no, s.email, s.phone
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            WHERE f.pending_amount > 0
            ORDER BY f.pending_amount DESC;
        """
        return fetch_all(query, (), db_path=self.db_path)

    def get_financial_kpi_summary(self) -> Dict[str, Any]:
        """Aggregate total revenue, collected funds, and outstanding dues."""
        return get_fee_collection_summary(db_path=self.db_path)
