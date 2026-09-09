"""
Sorting Algorithms implementation with comparison and step instrumentation.
Demonstrates Bubble Sort, Selection Sort, and Merge Sort with multi-attribute key support
and time/space complexity analysis.
"""

from typing import Any, Callable, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def bubble_sort(
    data: List[T],
    key_func: Optional[Callable[[T], Any]] = None,
    reverse: bool = False,
    key: Optional[Callable[[T], Any]] = None
) -> Tuple[List[T], int]:
    """
    Bubble Sort Algorithm.
    Repeatedly steps through the list, compares adjacent elements and swaps them if in wrong order.
    Includes optimization flag 'swapped' for early termination if already sorted.

    Complexity Analysis:
        - Time Complexity:
            * Best Case: O(n) [already sorted, terminates on pass 1]
            * Worst Case: O(n^2) [reverse sorted, requires n*(n-1)/2 comparisons and swaps]
            * Average Case: O(n^2)
        - Auxiliary Space Complexity: O(1) [in-place swap on copy]
        - Stability: Stable (equal elements retain relative order)
    """
    fn = key if key is not None else key_func
    arr = list(data)
    n = len(arr)
    comparisons = 0

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            val_a = fn(arr[j]) if fn else arr[j]
            val_b = fn(arr[j + 1]) if fn else arr[j + 1]

            condition = (val_a < val_b) if reverse else (val_a > val_b)
            if condition:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        if not swapped:
            break

    return arr, comparisons


def selection_sort(
    data: List[T],
    key_func: Optional[Callable[[T], Any]] = None,
    reverse: bool = False,
    key: Optional[Callable[[T], Any]] = None
) -> Tuple[List[T], int]:
    """
    Selection Sort Algorithm.
    Divides list into sorted and unsorted subarrays. Repeatedly finds minimum (or maximum)
    element from unsorted subarray and swaps it with the first unsorted element.

    Complexity Analysis:
        - Time Complexity:
            * Best Case: O(n^2) [always performs n*(n-1)/2 comparisons regardless of initial order]
            * Worst Case: O(n^2)
            * Average Case: O(n^2)
        - Auxiliary Space Complexity: O(1)
        - Stability: Not inherently stable (can swap non-adjacent identical keys)
    """
    fn = key if key is not None else key_func
    arr = list(data)
    n = len(arr)
    comparisons = 0

    for i in range(n):
        target_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            val_j = fn(arr[j]) if fn else arr[j]
            val_target = fn(arr[target_idx]) if fn else arr[target_idx]

            condition = (val_j > val_target) if reverse else (val_j < val_target)
            if condition:
                target_idx = j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]

    return arr, comparisons


def merge_sort(
    data: List[T],
    key_func: Optional[Callable[[T], Any]] = None,
    reverse: bool = False,
    key: Optional[Callable[[T], Any]] = None
) -> Tuple[List[T], int]:
    """
    Merge Sort (Divide and Conquer) Algorithm.
    Recursively splits the collection into two equal halves until sublists reach size 1,
    then merges them in sorted order.

    Complexity Analysis:
        - Time Complexity:
            * Best Case: O(n log2 n)
            * Worst Case: O(n log2 n)
            * Average Case: O(n log2 n)
        - Auxiliary Space Complexity: O(n) [requires buffer arrays during merge]
        - Stability: Stable (merging preserves initial index ordering of equal keys)
    """
    fn = key if key is not None else key_func
    total_comparisons = 0

    def _merge_sort_recursive(items: List[T]) -> List[T]:
        nonlocal total_comparisons
        if len(items) <= 1:
            return items

        mid = len(items) // 2
        left = _merge_sort_recursive(items[:mid])
        right = _merge_sort_recursive(items[mid:])

        # Merge step
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            total_comparisons += 1
            val_left = fn(left[i]) if fn else left[i]
            val_right = fn(right[j]) if fn else right[j]

            condition = (val_left >= val_right) if reverse else (val_left <= val_right)
            if condition:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    sorted_arr = _merge_sort_recursive(list(data))
    return sorted_arr, total_comparisons


# ==========================================
# Multi-Attribute Key Selector Helpers
# ==========================================

def key_by_name(record: Any) -> str:
    """Extract name from dict or model object for sorting."""
    if isinstance(record, dict):
        return record.get("name", "").lower()
    return getattr(record, "name", "").lower()


def key_by_roll_no(record: Any) -> str:
    """Extract roll number for sorting."""
    if isinstance(record, dict):
        return record.get("roll_no", "")
    return getattr(record, "roll_no", "")


def key_by_marks(record: Any) -> float:
    """Extract marks or score for sorting."""
    if isinstance(record, dict):
        return float(record.get("marks_obtained", record.get("percentage", 0.0)))
    return float(getattr(record, "marks_obtained", getattr(record, "percentage", 0.0)))


def key_by_attendance(record: Any) -> float:
    """Extract attendance percentage for sorting."""
    if isinstance(record, dict):
        return float(record.get("attendance_percentage", 0.0))
    return float(getattr(record, "attendance_percentage", 0.0))
