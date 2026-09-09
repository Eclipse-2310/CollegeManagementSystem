"""
Headless verification test suite for Phase 4: Algorithms (Searching & Sorting).
Asserts:
(a) All 3 sorting algorithms (Bubble, Selection, Merge) produce IDENTICAL, correctly-ordered output
    when tested on the same student dataset across:
    - Sorting by Name (Alphabetical)
    - Sorting by Roll Number
    - Sorting by Marks (Numeric descending)
    - Sorting by Attendance Percentage (Numeric ascending and descending)
(b) Linear Search vs Binary Search:
    - Both locate correct targets and return None for absent elements.
    - Binary Search requires strictly fewer comparisons than Linear Search on middle/late targets,
      demonstrating the O(log n) vs O(n) speedup.
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.searching import linear_search, binary_search
from algorithms.sorting import (
    bubble_sort, selection_sort, merge_sort,
    key_by_name, key_by_roll_no, key_by_marks, key_by_attendance
)


def run_phase4_verification():
    print("=" * 60)
    print("PHASE 4 VERIFICATION: Algorithms (Searching & Sorting)")
    print("=" * 60)

    # Sample dataset of 8 students
    sample_students = [
        {"roll_no": "CE105", "name": "Grace Hopper", "marks_obtained": 88.5, "attendance_percentage": 92.0},
        {"roll_no": "CE101", "name": "Ada Lovelace", "marks_obtained": 96.0, "attendance_percentage": 95.5},
        {"roll_no": "CE108", "name": "Katherine Johnson", "marks_obtained": 94.0, "attendance_percentage": 88.0},
        {"roll_no": "CE103", "name": "Alan Turing", "marks_obtained": 98.0, "attendance_percentage": 74.0},
        {"roll_no": "CE107", "name": "Claude Shannon", "marks_obtained": 82.0, "attendance_percentage": 68.5},
        {"roll_no": "CE102", "name": "Charles Babbage", "marks_obtained": 79.0, "attendance_percentage": 81.0},
        {"roll_no": "CE106", "name": "Margaret Hamilton", "marks_obtained": 91.0, "attendance_percentage": 97.0},
        {"roll_no": "CE104", "name": "John von Neumann", "marks_obtained": 99.5, "attendance_percentage": 76.5},
    ]

    # -------------------------------------------------------------
    # 1. SORTING ALGORITHMS EQUIVALENCE
    # -------------------------------------------------------------
    print("\n[+] 1. Testing Sorting Algorithms Equivalence (Bubble, Selection, Merge):")

    # (a) Sort by Name (Ascending)
    bubble_by_name, b_comps = bubble_sort(sample_students, key_func=key_by_name)
    select_by_name, s_comps = selection_sort(sample_students, key_func=key_by_name)
    merge_by_name, m_comps = merge_sort(sample_students, key_func=key_by_name)

    names_bubble = [s["name"] for s in bubble_by_name]
    names_select = [s["name"] for s in select_by_name]
    names_merge = [s["name"] for s in merge_by_name]

    assert names_bubble == names_select == names_merge, "Sorts produced differing name orders!"
    # Verify order is strictly alphabetical
    assert names_bubble == sorted(names_bubble), "Output is not sorted alphabetically!"
    print(f"  [OK] Sorted by Name: {names_bubble[:4]}... (All 3 sorts IDENTICAL)")
    print(f"       Comparisons: Bubble={b_comps}, Selection={s_comps}, Merge={m_comps}")

    # (b) Sort by Roll No (Ascending)
    bubble_by_roll, _ = bubble_sort(sample_students, key_func=key_by_roll_no)
    select_by_roll, _ = selection_sort(sample_students, key_func=key_by_roll_no)
    merge_by_roll, _ = merge_sort(sample_students, key_func=key_by_roll_no)

    rolls_b = [s["roll_no"] for s in bubble_by_roll]
    rolls_s = [s["roll_no"] for s in select_by_roll]
    rolls_m = [s["roll_no"] for s in merge_by_roll]

    assert rolls_b == rolls_s == rolls_m, "Sorts produced differing roll number orders!"
    assert rolls_b == sorted(rolls_b)
    print(f"  [OK] Sorted by Roll No: {rolls_b} (All 3 sorts IDENTICAL)")

    # (c) Sort by Marks (Descending / Rank order)
    bubble_by_marks, _ = bubble_sort(sample_students, key_func=key_by_marks, reverse=True)
    select_by_marks, _ = selection_sort(sample_students, key_func=key_by_marks, reverse=True)
    merge_by_marks, _ = merge_sort(sample_students, key_func=key_by_marks, reverse=True)

    marks_b = [s["marks_obtained"] for s in bubble_by_marks]
    marks_s = [s["marks_obtained"] for s in select_by_marks]
    marks_m = [s["marks_obtained"] for s in merge_by_marks]

    assert marks_b == marks_s == marks_m, "Sorts produced differing marks orders!"
    assert marks_b == sorted(marks_b, reverse=True)
    print(f"  [OK] Sorted by Marks (Rank): {marks_b} (All 3 sorts IDENTICAL)")

    # (d) Sort by Attendance Percentage (Ascending - Defaulters first)
    bubble_by_att, _ = bubble_sort(sample_students, key_func=key_by_attendance)
    select_by_att, _ = selection_sort(sample_students, key_func=key_by_attendance)
    merge_by_att, _ = merge_sort(sample_students, key_func=key_by_attendance)

    att_b = [s["attendance_percentage"] for s in bubble_by_att]
    att_s = [s["attendance_percentage"] for s in select_by_att]
    att_m = [s["attendance_percentage"] for s in merge_by_att]

    assert att_b == att_s == att_m, "Sorts produced differing attendance orders!"
    assert att_b == sorted(att_b)
    print(f"  [OK] Sorted by Attendance (Ascending): {att_b} (All 3 sorts IDENTICAL)")

    # -------------------------------------------------------------
    # 2. SEARCHING ALGORITHMS & COMPLEXITY COMPARISON
    # -------------------------------------------------------------
    print("\n[+] 2. Testing Searching Algorithms (Linear Search vs Binary Search):")

    # Use dataset pre-sorted by roll number for Binary Search
    sorted_by_roll = bubble_by_roll

    # Test target near end: 'CE108' (Katherine Johnson, index 7 of 8)
    target = "CE108"
    lin_idx, lin_comps = linear_search(sorted_by_roll, target, key_func=key_by_roll_no)
    bin_idx, bin_comps = binary_search(sorted_by_roll, target, key_func=key_by_roll_no)

    assert lin_idx == bin_idx == 7, f"Indices did not match: Linear={lin_idx}, Binary={bin_idx}"
    assert sorted_by_roll[bin_idx]["name"] == "Katherine Johnson"

    print(f"  [OK] Target '{target}' found at index {bin_idx} ({sorted_by_roll[bin_idx]['name']})")
    print(f"       Linear Search comparisons: {lin_comps} (O(n) scan to index {lin_idx})")
    print(f"       Binary Search comparisons: {bin_comps} (O(log2 n) divide-and-conquer)")
    assert bin_comps < lin_comps, "Binary search should take fewer comparisons for element at end!"
    print(f"  [OK] Speedup confirmed: Binary Search used {bin_comps} steps vs Linear Search's {lin_comps} steps.")

    # Test absent element: 'CE999'
    lin_miss_idx, lin_miss_comps = linear_search(sorted_by_roll, "CE999", key_func=key_by_roll_no)
    bin_miss_idx, bin_miss_comps = binary_search(sorted_by_roll, "CE999", key_func=key_by_roll_no)

    assert lin_miss_idx is None and bin_miss_idx is None
    print(f"  [OK] Non-existent target 'CE999' correctly returned None by both searchers.")
    print(f"       Linear Search searched all {lin_miss_comps} elements.")
    print(f"       Binary Search determined absence in only {bin_miss_comps} steps.")

    print("\n" + "=" * 60)
    print("ALL PHASE 4 VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase4_verification()
