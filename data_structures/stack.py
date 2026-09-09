"""
Custom Stack Data Structure implementation (LIFO - Last In First Out).
Genuinely wired into the system for Action History and Undo operations.
"""

from typing import Any, Callable, Generic, List, Optional, TypeVar

T = TypeVar("T")


class ActionRecord:
    """
    Represents an undoable action in the CMS.
    Contains metadata and a rollback callback function for true undo capabilities.
    """

    def __init__(self, action_type: str, description: str, entity_type: str, entity_id: Any, rollback_fn: Optional[Callable[[], Any]] = None, payload: Optional[Any] = None):
        self.action_type = action_type        # e.g., 'ADD_STUDENT', 'UPDATE_STUDENT', 'UPDATE_MARKS'
        self.description = description        # e.g., "Enrolled student Ada Lovelace (CS101)"
        self.entity_type = entity_type        # e.g., "Student", "Mark"
        self.entity_id = entity_id            # e.g., student_id = 15
        self.rollback_fn = rollback_fn        # Callable to undo the action
        self.payload = payload                # Previous state snapshot for restoration

    def undo(self) -> Any:
        """Executes the inverse operation to revert the action."""
        if self.rollback_fn:
            return self.rollback_fn()
        return None

    def __repr__(self) -> str:
        return f"<ActionRecord type='{self.action_type}' entity={self.entity_type}#{self.entity_id} desc='{self.description}'>"


class Stack(Generic[T]):
    """
    Generic LIFO Stack data structure.
    Time Complexity:
        - push: O(1)
        - pop: O(1)
        - peek: O(1)
        - is_empty: O(1)
        - size: O(1)
    """

    def __init__(self, max_size: int = 100, capacity: Optional[int] = None):
        self._items: List[T] = []
        self._max_size = capacity if capacity is not None else max_size

    def push(self, item: T) -> None:
        """
        Push item onto top of stack.
        If max_size reached, evicts the oldest item (bottom) to maintain bounded history.
        Time Complexity: O(1) amortized.
        """
        if len(self._items) >= self._max_size:
            self._items.pop(0)  # Remove oldest to maintain buffer limit
        self._items.append(item)

    def pop(self) -> T:
        """
        Remove and return the top item.
        Raises IndexError if stack is empty.
        Time Complexity: O(1).
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> Optional[T]:
        """
        Return the top item without removing it.
        Time Complexity: O(1).
        """
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        """Return True if the stack contains zero elements."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of elements in the stack."""
        return len(self._items)

    def clear(self) -> None:
        """Remove all elements from the stack."""
        self._items.clear()

    @property
    def capacity(self) -> int:
        return self._max_size

    def items(self) -> List[T]:
        """Return a shallow copy of stack elements from bottom to top."""
        return list(self._items)

    def to_list(self) -> List[T]:
        """Return a shallow copy of stack elements from bottom to top."""
        return list(self._items)

    def __repr__(self) -> str:
        return f"<Stack size={len(self._items)} top={self.peek() if not self.is_empty() else 'None'}>"


# Convenient Alias
UndoStack = Stack
