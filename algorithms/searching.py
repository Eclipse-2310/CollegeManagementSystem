"""
Searching Algorithms implementation with step/comparison instrumentation.
Demonstrates Linear Search vs Binary Search with asymptotic complexity analysis.
"""

from typing import Any, Callable, List, Optional, Tuple, TypeVar

T = TypeVar("T")


def linear_search(
    data: List[T],
    target: Any,
    key_func: Optional[Callable[[T], Any]] = None
) -> Tuple[Optional[int], int]:
    """
    Linear Search (Sequential Search) Algorithm.
    Iterates sequentially through the collection from index 0 to n-1.
    
    Parameters:
        data: List of elements to search.
        target: Value being searched for.
        key_func: Optional function to extract comparison key from element.
        
    Returns:
        Tuple of (found_index, comparison_count). If not found, found_index is None.

    Complexity Analysis:
        - Time Complexity:
            * Best Case: O(1) [target is the first element]
            * Worst Case: O(n) [target is the last element or absent]
            * Average Case: O(n/2) = O(n) [target is midway through list]
        - Auxiliary Space Complexity: O(1) [in-place iterative pointer]
        - Pre-conditions: None (operates on unsorted or sorted data)
    """
    comparisons = 0
    for i, item in enumerate(data):
        comparisons += 1
        val = key_func(item) if key_func else item
        if val == target:
            return i, comparisons
    return None, comparisons


def binary_search(
    data: List[T],
    target: Any,
    key_func: Optional[Callable[[T], Any]] = None
) -> Tuple[Optional[int], int]:
    """
    Binary Search (Divide-and-Conquer) Algorithm.
    Repeatedly halves the search interval by comparing target to middle element.
    
    CRITICAL REQUIREMENT:
        The input collection MUST be sorted in ascending order by key_func!
    
    Parameters:
        data: Pre-sorted list of elements.
        target: Value being searched for.
        key_func: Optional function to extract comparison key from element.
        
    Returns:
        Tuple of (found_index, comparison_count). If not found, found_index is None.

    Complexity Analysis:
        - Time Complexity:
            * Best Case: O(1) [target is exact middle element]
            * Worst Case: O(log2 n) [interval halved each step until 1 element]
            * Average Case: O(log2 n)
        - Auxiliary Space Complexity: O(1) [iterative implementation]
        
    Trade-Off Analysis (Viva Evaluation Highlight):
        - Linear Search: O(n) time, 0 preparation cost. Ideal for small or frequently updated unsorted lists.
        - Binary Search: O(log n) time, requires O(n log n) sorting phase initially. Exponentially faster
          for large static or read-heavy datasets (e.g. for 1,000,000 items, Linear Search takes up to
          1,000,000 checks, whereas Binary Search takes at most 20 checks!).
    """
    low = 0
    high = len(data) - 1
    comparisons = 0

    while low <= high:
        mid = (low + high) // 2
        comparisons += 1
        mid_val = key_func(data[mid]) if key_func else data[mid]

        if mid_val == target:
            return mid, comparisons
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return None, comparisons
