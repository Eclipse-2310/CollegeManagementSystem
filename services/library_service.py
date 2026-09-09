"""
Library Service module for College Management System.
Integrates Database persistence with custom Queue data structure (FIFO)
for handling pending book issue requests and reservations.
"""

from typing import Any, Dict, List, Optional
import datetime

from database.database import (
    execute_query, fetch_all, fetch_one, DEFAULT_DB_PATH
)
from models.other_models import LibraryBook, LibraryTransaction
from data_structures.queue import Queue, ServiceRequest


class LibraryService:
    """
    Manages library book inventory, circulation transactions,
    and a FIFO Queue for pending reservations.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

        # DATA STRUCTURE 2: FIFO Queue for Pending Issue & Reservation Requests
        self.request_queue: Queue[ServiceRequest] = Queue[ServiceRequest]()

    def get_all_books(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all books in catalog with optional title/author/ISBN search."""
        query = "SELECT * FROM library_books WHERE 1=1"
        params = []
        if search:
            query += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ? OR category LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term, term, term])
        query += " ORDER BY title ASC"
        return fetch_all(query, tuple(params), db_path=self.db_path)

    def add_book(self, book: LibraryBook) -> int:
        """Add a new book to the library catalog."""
        query = """
            INSERT INTO library_books (title, author, category, isbn, quantity)
            VALUES (?, ?, ?, ?, ?);
        """
        params = (book.title, book.author, book.category, book.isbn, book.quantity)
        return execute_query(query, params, db_path=self.db_path)

    def issue_book(self, book_id: int, student_id: int, issue_date: Optional[str] = None) -> int:
        """
        Issue a book copy to a student, decrementing available quantity.
        """
        book = fetch_one("SELECT * FROM library_books WHERE book_id = ?", (book_id,), db_path=self.db_path)
        if not book:
            raise ValueError(f"Book #{book_id} not found.")
        if book["quantity"] <= 0:
            raise ValueError(f"Book '{book['title']}' is currently out of stock. Please queue a reservation.")

        date_str = issue_date or datetime.date.today().isoformat()
        trans_query = """
            INSERT INTO library_transactions (book_id, student_id, issue_date, status)
            VALUES (?, ?, ?, 'Issued');
        """
        trans_id = execute_query(trans_query, (book_id, student_id, date_str), db_path=self.db_path)

        # Decrement quantity
        execute_query("UPDATE library_books SET quantity = quantity - 1 WHERE book_id = ?", (book_id,), db_path=self.db_path)
        return trans_id

    def return_book(self, transaction_id: int, return_date: Optional[str] = None) -> bool:
        """
        Record the return of a book and increment available quantity.
        """
        trans = fetch_one("SELECT * FROM library_transactions WHERE transaction_id = ?", (transaction_id,), db_path=self.db_path)
        if not trans:
            raise ValueError(f"Transaction #{transaction_id} not found.")
        if trans["status"] == "Returned":
            return False

        date_str = return_date or datetime.date.today().isoformat()
        execute_query(
            "UPDATE library_transactions SET status = 'Returned', return_date = ? WHERE transaction_id = ?",
            (date_str, transaction_id), db_path=self.db_path
        )
        # Increment quantity
        execute_query("UPDATE library_books SET quantity = quantity + 1 WHERE book_id = ?", (trans["book_id"],), db_path=self.db_path)
        return True

    def get_active_transactions(self, student_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve active and historical library transactions."""
        query = """
            SELECT lt.*, b.title, b.author, b.isbn, s.name AS student_name, s.roll_no
            FROM library_transactions lt
            JOIN library_books b ON lt.book_id = b.book_id
            JOIN students s ON lt.student_id = s.student_id
            WHERE 1=1
        """
        params = []
        if student_id:
            query += " AND lt.student_id = ?"
            params.append(student_id)
        query += " ORDER BY lt.issue_date DESC"
        return fetch_all(query, tuple(params), db_path=self.db_path)

    # ==========================================
    # Queue Integration: Pending Issue Requests
    # ==========================================

    def queue_issue_request(self, requester_name: str, book_isbn: str, notes: str = "") -> ServiceRequest:
        """
        Enqueue a book request when a copy is currently checked out or pending admin approval.
        Demonstrates FIFO Queue operation.
        """
        req_id = f"REQ-{self.request_queue.size() + 101}"
        req = ServiceRequest(
            request_id=req_id,
            request_type="BOOK_RESERVATION",
            requester_name=requester_name,
            details=f"Book ISBN: {book_isbn} | Notes: {notes}"
        )
        self.request_queue.enqueue(req)
        return req

    def process_next_request(self) -> Optional[ServiceRequest]:
        """
        Process the oldest pending request from the FIFO queue.
        Time Complexity: O(1) front, O(n) array shift.
        """
        if self.request_queue.is_empty():
            return None
        processed_req = self.request_queue.dequeue()
        processed_req.status = "Processed"
        return processed_req
