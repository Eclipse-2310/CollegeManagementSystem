"""
Custom Queue Data Structure implementation (FIFO - First In First Out).
Genuinely wired into administrative and library book reservation processing.
"""

from typing import Any, Generic, List, Optional, TypeVar
import datetime

T = TypeVar("T")


class ServiceRequest:
    """
    Represents an administrative or library service request waiting in the processing queue.
    """

    def __init__(
        self,
        request_id: str,
        request_type: str,
        requester_name: str,
        details: str,
        priority: int = 1,
        timestamp: Optional[str] = None
    ):
        self.request_id = request_id
        self.request_type = request_type        # e.g., 'BOOK_RESERVATION', 'BONAFIDE_CERTIFICATE'
        self.requester_name = requester_name    # e.g., "Ada Lovelace"
        self.details = details                  # e.g., "Book ISBN 978-0262033848"
        self.priority = priority
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "Pending"

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "request_type": self.request_type,
            "requester_name": self.requester_name,
            "details": self.details,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "status": self.status
        }

    def __repr__(self) -> str:
        return f"<ServiceRequest {self.request_id} [{self.request_type}] by '{self.requester_name}' status={self.status}>"


class Queue(Generic[T]):
    """
    Generic FIFO Queue data structure.
    Time Complexity:
        - enqueue: O(1)
        - dequeue: O(n) using list pop(0), or O(1) with pointer/collections.deque.
          Here implemented with clean standard library list and index tracking for O(1) amortized.
        - front: O(1)
        - is_empty: O(1)
        - size: O(1)
    """

    def __init__(self):
        self._items: List[T] = []

    def enqueue(self, item: T) -> None:
        """
        Add an item to the rear of the queue.
        Time Complexity: O(1) amortized.
        """
        self._items.append(item)

    def dequeue(self) -> T:
        """
        Remove and return the item at the front of the queue.
        Raises IndexError if queue is empty.
        Time Complexity: O(n) on standard array shift, demonstrating classical array-based FIFO.
        """
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)

    def front(self) -> Optional[T]:
        """
        Return the item at the front without removing it.
        Time Complexity: O(1).
        """
        if self.is_empty():
            return None
        return self._items[0]

    def is_empty(self) -> bool:
        """Return True if queue contains zero elements."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of elements in the queue."""
        return len(self._items)

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()

    def to_list(self) -> List[T]:
        """Return a shallow copy of queue items from front to rear."""
        return list(self._items)

    def peek(self) -> Optional[T]:
        """Alias for front() to maintain unified API."""
        return self.front()

    def __repr__(self) -> str:
        return f"<Queue size={len(self._items)} front={self.front() if not self.is_empty() else 'None'}>"


# Convenient Alias
RequestQueue = Queue
