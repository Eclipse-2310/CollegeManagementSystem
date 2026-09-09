"""
Custom Doubly LinkedList Data Structure implementation with Node pointers.
Genuinely wired into the Campus Notice Board for dynamic ordering and fast insertions.
"""

from typing import Any, Callable, Generic, Iterator, List, Optional, TypeVar

T = TypeVar("T")


class Node(Generic[T]):
    """
    Doubly-linked Node storing data and bidirectional pointers (prev, next).
    """

    def __init__(self, data: T, prev_node: Optional["Node[T]"] = None, next_node: Optional["Node[T]"] = None):
        self.data: T = data
        self.prev: Optional["Node[T]"] = prev_node
        self.next: Optional["Node[T]"] = next_node

    def __repr__(self) -> str:
        return f"<Node data={self.data}>"


class DoublyLinkedList(Generic[T]):
    """
    Doubly Linked List data structure.
    Time Complexity:
        - insert_front: O(1)
        - insert_rear: O(1)
        - delete: O(n) search + O(1) pointer reconnection
        - search: O(n)
        - traverse: O(n)
        - size: O(1)
    """

    def __init__(self):
        self.head: Optional[Node[T]] = None
        self.tail: Optional[Node[T]] = None
        self._size: int = 0

    def insert_front(self, data: T) -> Node[T]:
        """
        Insert data at the head of the list.
        Used for campus notices so latest announcements appear first.
        Time Complexity: O(1).
        """
        new_node = Node(data, prev_node=None, next_node=self.head)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.head.prev = new_node
            self.head = new_node
        self._size += 1
        return new_node

    def insert_rear(self, data: T) -> Node[T]:
        """
        Insert data at the tail of the list.
        Time Complexity: O(1).
        """
        new_node = Node(data, prev_node=self.tail, next_node=None)
        if self.tail is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1
        return new_node

    def delete(self, predicate: Callable[[T], bool]) -> bool:
        """
        Find and remove the first node whose data satisfies predicate(data) == True.
        Re-links neighboring nodes' prev and next pointers.
        Time Complexity: O(n) traversal, O(1) splice.
        """
        current = self.head
        while current is not None:
            if predicate(current.data):
                # Unlink current node
                if current.prev is not None:
                    current.prev.next = current.next
                else:
                    self.head = current.next  # Removing head

                if current.next is not None:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev  # Removing tail

                self._size -= 1
                return True
            current = current.next
        return False

    def search(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """
        Linear search along the linked list.
        Time Complexity: O(n).
        """
        current = self.head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def traverse(self, forward: bool = True) -> Iterator[T]:
        """
        Iterate over list elements.
        forward=True walks from head to tail.
        forward=False walks from tail to head.
        Time Complexity: O(n).
        """
        if forward:
            curr = self.head
            while curr is not None:
                yield curr.data
                curr = curr.next
        else:
            curr = self.tail
            while curr is not None:
                yield curr.data
                curr = curr.prev

    def to_list(self) -> List[T]:
        """Convert linked chain to standard Python list."""
        return list(self.traverse(forward=True))

    def size(self) -> int:
        """Return the number of nodes in O(1)."""
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def clear(self) -> None:
        self.head = None
        self.tail = None
        self._size = 0

    def __repr__(self) -> str:
        return f"<DoublyLinkedList size={self._size} head={self.head.data if self.head else 'None'}>"

    # Convenience aliases
    insert_end = insert_rear
    insert_beginning = insert_front
    append = insert_rear
    prepend = insert_front
