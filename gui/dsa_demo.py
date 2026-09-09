r"""
DSA Demonstration Panel for College Management System.
Provides an interactive, visual Academic Viva panel demonstrating:
1. Stack (LIFO) - Multi-step Undo & Action History ($O(1)$)
2. Queue (FIFO) - Request & Approval Pipeline ($O(1)$)
3. Doubly Linked List - Bidirectional Notice Board Chain
4. Searching Benchmark - Linear Search $O(n)$ vs Binary Search $O(\log n)$
5. Sorting Benchmark - Bubble Sort, Selection Sort, and Merge Sort ($O(n^2)$ vs $O(n \log n)$)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Dict, List, Optional
import time

from gui.styles import PALETTE, FONTS
from data_structures.stack import UndoStack
from data_structures.queue import RequestQueue
from data_structures.linked_list import DoublyLinkedList
from algorithms.searching import linear_search, binary_search
from algorithms.sorting import bubble_sort, selection_sort, merge_sort
from database.database import DEFAULT_DB_PATH, fetch_all
from services.student_service import StudentService
from services.admin_service import AdminService
from services.marks_service import MarksService


class DSADemoScreen(tk.Frame):
    """
    Academic Viva demonstration screen for Data Structures & Algorithms.
    """

    def __init__(self, parent, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.db_path = db_path or DEFAULT_DB_PATH
        self.student_svc = StudentService(db_path=self.db_path)
        self.admin_svc = AdminService(db_path=self.db_path)
        self.marks_svc = MarksService(db_path=self.db_path)

        # Standalone data structures for live interactive manipulation
        self.demo_stack = UndoStack[str](capacity=10)
        self.demo_queue = RequestQueue[str]()
        self.demo_ll = DoublyLinkedList[str]()

        # Prepopulate demo data structures
        self._seed_demo_ds()

        self._build_ui()

    def _seed_demo_ds(self):
        # Stack initial states
        self.demo_stack.push("UPDATE: Student CE101 email updated")
        self.demo_stack.push("INSERT: Student CE105 enrolled")
        self.demo_stack.push("FEE: Payment ₹25,000 received for CE102")

        # Queue initial requests
        self.demo_queue.enqueue("REQ-101: Library Book Issue - CLRS Algorithms (Student CE101)")
        self.demo_queue.enqueue("REQ-102: Hall Ticket Generation Request (Student IT103)")
        self.demo_queue.enqueue("REQ-103: Bonafide Certificate Application (Student EX102)")

        # Linked list initial nodes
        self.demo_ll.insert_end("Notice 1: Semester Registration Open")
        self.demo_ll.insert_end("Notice 2: Midterm Timetable Published")
        self.demo_ll.insert_end("Notice 3: Guest Lecture on Agentic AI")

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)

        title_row = tk.Frame(title_box, bg=PALETTE["bg_main"])
        title_row.pack(anchor="w")
        tk.Label(title_row, text="🔬", font=("Segoe UI", 18), bg=PALETTE["bg_main"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(title_row, text="Data Structures & Algorithms Viva Panel", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="Interactive verification of Stack, Queue, Doubly Linked List, Search & Sort Complexity",
            font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]
        ).pack(anchor="w", pady=(2, 0))

        # Academic Badge
        tk.Label(
            header, text="SE ENGINEERING VIVA EVALUATION", font=FONTS["small"],
            fg=PALETTE["primary"], bg=PALETTE["primary_light"], padx=10, pady=5
        ).pack(side=tk.RIGHT)

        # Tabbed Notebook
        notebook_frame = tk.Frame(self, bg=PALETTE["bg_main"])
        notebook_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 15))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create Tabs
        self.tab_stack = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_queue = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_ll = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_search = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)
        self.tab_sort = tk.Frame(self.notebook, bg=PALETTE["bg_card"], padx=20, pady=15)

        self.notebook.add(self.tab_stack, text="  📚 Stack (Undo History)  ")
        self.notebook.add(self.tab_queue, text="  📬 Queue (Requests)  ")
        self.notebook.add(self.tab_ll, text="  🔗 Doubly Linked List  ")
        self.notebook.add(self.tab_search, text="  🔍 Searching Benchmark  ")
        self.notebook.add(self.tab_sort, text="  ⚡ Sorting Benchmark  ")

        # Build each tab
        self._build_stack_tab()
        self._build_queue_tab()
        self._build_ll_tab()
        self._build_search_tab()
        self._build_sort_tab()

    # ==========================================
    # Tab 1: Stack Visualizer
    # ==========================================
    def _build_stack_tab(self):
        # Info & controls
        top_bar = tk.Frame(self.tab_stack, bg=PALETTE["bg_card"])
        top_bar.pack(fill=tk.X, pady=(0, 15))

        info_box = tk.Frame(top_bar, bg="#EEF2FF", padx=12, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        tk.Label(info_box, text="Principle: LIFO (Last In First Out) | Push: O(1) | Pop: O(1) | Peek: O(1)", font=FONTS["body_bold"], fg=PALETTE["primary"], bg="#EEF2FF").pack(anchor="w")
        tk.Label(info_box, text="CMS Application: Tracks user state mutations for 1-click Undo operations across forms.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#EEF2FF").pack(anchor="w")

        # Input & buttons
        ctrl_frame = tk.Frame(self.tab_stack, bg=PALETTE["bg_card"])
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(ctrl_frame, text="Action Text:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))
        self.stack_input = ttk.Entry(ctrl_frame, width=35, font=FONTS["body"])
        self.stack_input.pack(side=tk.LEFT, padx=(0, 8))
        self.stack_input.insert(0, "EDIT: Student Phone updated")

        ttk.Button(ctrl_frame, text="Push Action (O(1))", style="Primary.TButton", command=self._stack_push).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Pop / Undo (O(1))", style="Secondary.TButton", command=self._stack_pop).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Peek Top", style="Secondary.TButton", command=self._stack_peek).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Clear", style="Secondary.TButton", command=self._stack_clear).pack(side=tk.LEFT, padx=3)

        # Status Label
        self.stack_status_lbl = tk.Label(self.tab_stack, text="Stack Ready", font=FONTS["body_bold"], fg=PALETTE["primary"], bg=PALETTE["bg_card"])
        self.stack_status_lbl.pack(anchor="w", pady=(0, 8))

        # Visual Container
        self.stack_canvas = tk.Frame(self.tab_stack, bg="#0F172A", padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        self.stack_canvas.pack(fill=tk.BOTH, expand=True)

        self._render_stack_visual()

    def _render_stack_visual(self):
        for widget in self.stack_canvas.winfo_children():
            widget.destroy()

        items = self.demo_stack.items() # list
        count = len(items)

        tk.Label(self.stack_canvas, text=f"STACK MEMORY LAYOUT (Capacity: {self.demo_stack.capacity}, Current Size: {count})", font=FONTS["small"], fg="#94A3B8", bg="#0F172A").pack(anchor="w", pady=(0, 10))

        if count == 0:
            tk.Label(self.stack_canvas, text="[ Stack is Empty - Underflow condition on Pop ]", font=FONTS["body"], fg="#EF4444", bg="#0F172A").pack(pady=40)
            return

        # Render elements top to bottom
        for idx in range(count - 1, -1, -1):
            is_top = (idx == count - 1)
            item_text = items[idx]

            bg_col = "#38BDF8" if is_top else "#1E293B"
            fg_col = "#0F172A" if is_top else "#F8FAFC"
            border_col = "#0284C7" if is_top else "#334155"

            box = tk.Frame(self.stack_canvas, bg=bg_col, padx=12, pady=8, highlightbackground=border_col, highlightthickness=1)
            box.pack(fill=tk.X, pady=3)

            prefix = "🔝 [TOP OF STACK] → " if is_top else f"    [Index {idx}] → "
            tk.Label(box, text=f"{prefix}{item_text}", font=FONTS["code"], fg=fg_col, bg=bg_col).pack(anchor="w")

    def _stack_push(self):
        val = self.stack_input.get().strip()
        if not val:
            return
        try:
            self.demo_stack.push(val)
            self.stack_status_lbl.config(text=f"✅ Pushed item onto stack: '{val}' [O(1)]", fg=PALETTE["success"])
            self._render_stack_visual()
        except OverflowError as e:
            self.stack_status_lbl.config(text=f"❌ {str(e)}", fg=PALETTE["danger"])

    def _stack_pop(self):
        try:
            val = self.demo_stack.pop()
            self.stack_status_lbl.config(text=f"↺ Popped / Undone item from stack: '{val}' [O(1)]", fg=PALETTE["warning"])
            self._render_stack_visual()
        except IndexError as e:
            self.stack_status_lbl.config(text=f"❌ {str(e)}", fg=PALETTE["danger"])

    def _stack_peek(self):
        try:
            val = self.demo_stack.peek()
            messagebox.showinfo("Stack Peek", f"Top element on stack:\n\n{val}\n\nOperation completed in O(1) time without modifying stack.")
        except IndexError:
            messagebox.showwarning("Stack Empty", "The stack is currently empty.")

    def _stack_clear(self):
        self.demo_stack.clear()
        self.stack_status_lbl.config(text="Stack cleared.", fg=PALETTE["text_secondary"])
        self._render_stack_visual()

    # ==========================================
    # Tab 2: Queue Visualizer
    # ==========================================
    def _build_queue_tab(self):
        top_bar = tk.Frame(self.tab_queue, bg=PALETTE["bg_card"])
        top_bar.pack(fill=tk.X, pady=(0, 15))

        info_box = tk.Frame(top_bar, bg="#ECFDF5", padx=12, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        tk.Label(info_box, text="Principle: FIFO (First In First Out) | Enqueue: O(1) | Dequeue: O(1) | Peek: O(1)", font=FONTS["body_bold"], fg=PALETTE["success"], bg="#ECFDF5").pack(anchor="w")
        tk.Label(info_box, text="CMS Application: Handles student library borrowing and administrative approval queues in fair arrival order.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#ECFDF5").pack(anchor="w")

        # Controls
        ctrl_frame = tk.Frame(self.tab_queue, bg=PALETTE["bg_card"])
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(ctrl_frame, text="Request Text:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))
        self.queue_input = ttk.Entry(ctrl_frame, width=35, font=FONTS["body"])
        self.queue_input.pack(side=tk.LEFT, padx=(0, 8))
        self.queue_input.insert(0, "REQ-104: Book Issue - Operating Systems")

        ttk.Button(ctrl_frame, text="Enqueue Request (O(1))", style="Primary.TButton", command=self._queue_enqueue).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Dequeue / Process (O(1))", style="Secondary.TButton", command=self._queue_dequeue).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Peek Front", style="Secondary.TButton", command=self._queue_peek).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Clear", style="Secondary.TButton", command=self._queue_clear).pack(side=tk.LEFT, padx=3)

        self.queue_status_lbl = tk.Label(self.tab_queue, text="Queue Ready", font=FONTS["body_bold"], fg=PALETTE["success"], bg=PALETTE["bg_card"])
        self.queue_status_lbl.pack(anchor="w", pady=(0, 8))

        self.queue_canvas = tk.Frame(self.tab_queue, bg="#0F172A", padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        self.queue_canvas.pack(fill=tk.BOTH, expand=True)

        self._render_queue_visual()

    def _render_queue_visual(self):
        for widget in self.queue_canvas.winfo_children():
            widget.destroy()

        items = self.demo_queue.to_list()
        count = len(items)

        tk.Label(self.queue_canvas, text=f"FIFO QUEUE PIPELINE (Pending Requests: {count})", font=FONTS["small"], fg="#94A3B8", bg="#0F172A").pack(anchor="w", pady=(0, 10))

        if count == 0:
            tk.Label(self.queue_canvas, text="[ Queue is Empty - No pending requests in pipeline ]", font=FONTS["body"], fg="#10B981", bg="#0F172A").pack(pady=40)
            return

        for idx, item_text in enumerate(items):
            is_front = (idx == 0)
            is_rear = (idx == count - 1)

            bg_col = "#34D399" if is_front else ("#60A5FA" if is_rear else "#1E293B")
            fg_col = "#0F172A" if (is_front or is_rear) else "#F8FAFC"

            tag = "FRONT (NEXT TO SERVE)" if is_front else ("REAR (NEWEST ARRIVAL)" if is_rear else f"POSITION {idx + 1}")

            box = tk.Frame(self.queue_canvas, bg=bg_col, padx=12, pady=7, highlightbackground="#334155", highlightthickness=1)
            box.pack(fill=tk.X, pady=3)

            tk.Label(box, text=f"[{tag}] ➔ {item_text}", font=FONTS["code"], fg=fg_col, bg=bg_col).pack(anchor="w")

    def _queue_enqueue(self):
        val = self.queue_input.get().strip()
        if not val:
            return
        self.demo_queue.enqueue(val)
        self.queue_status_lbl.config(text=f"✅ Enqueued to rear: '{val}' [O(1)]", fg=PALETTE["success"])
        self._render_queue_visual()

    def _queue_dequeue(self):
        val = self.demo_queue.dequeue()
        if val is None:
            self.queue_status_lbl.config(text="❌ Queue Underflow: No requests to process", fg=PALETTE["danger"])
        else:
            self.queue_status_lbl.config(text=f"⚡ Dequeued and Processed front: '{val}' [O(1)]", fg=PALETTE["primary"])
            self._render_queue_visual()

    def _queue_peek(self):
        val = self.demo_queue.peek()
        if val:
            messagebox.showinfo("Queue Peek", f"Front element in queue:\n\n{val}\n\nRetrieved in O(1) time.")
        else:
            messagebox.showwarning("Queue Empty", "The queue is currently empty.")

    def _queue_clear(self):
        self.demo_queue.clear()
        self.queue_status_lbl.config(text="Queue cleared.", fg=PALETTE["text_secondary"])
        self._render_queue_visual()

    # ==========================================
    # Tab 3: Doubly Linked List Visualizer
    # ==========================================
    def _build_ll_tab(self):
        top_bar = tk.Frame(self.tab_ll, bg=PALETTE["bg_card"])
        top_bar.pack(fill=tk.X, pady=(0, 15))

        info_box = tk.Frame(top_bar, bg="#FFFBEB", padx=12, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        tk.Label(info_box, text="Architecture: Doubly Linked List | Insert Front: O(1) | Delete: O(n) search + O(1) unlink", font=FONTS["body_bold"], fg="#D97706", bg="#FFFBEB").pack(anchor="w")
        tk.Label(info_box, text="CMS Application: Powers the Campus Notice Board chain with instantaneous O(1) announcement prepending.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#FFFBEB").pack(anchor="w")

        # Controls
        ctrl_frame = tk.Frame(self.tab_ll, bg=PALETTE["bg_card"])
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(ctrl_frame, text="Notice Node:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))
        self.ll_input = ttk.Entry(ctrl_frame, width=32, font=FONTS["body"])
        self.ll_input.pack(side=tk.LEFT, padx=(0, 8))
        self.ll_input.insert(0, "Notice: Sports Day Registration")

        ttk.Button(ctrl_frame, text="Prepend Head (O(1))", style="Primary.TButton", command=self._ll_insert_front).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Append Tail (O(1))", style="Secondary.TButton", command=self._ll_insert_end).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Traverse Chain", style="Secondary.TButton", command=self._ll_traverse).pack(side=tk.LEFT, padx=3)
        ttk.Button(ctrl_frame, text="Clear Chain", style="Secondary.TButton", command=self._ll_clear).pack(side=tk.LEFT, padx=3)

        self.ll_status_lbl = tk.Label(self.tab_ll, text="Doubly Linked List Ready", font=FONTS["body_bold"], fg="#D97706", bg=PALETTE["bg_card"])
        self.ll_status_lbl.pack(anchor="w", pady=(0, 8))

        self.ll_canvas = tk.Frame(self.tab_ll, bg="#0F172A", padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        self.ll_canvas.pack(fill=tk.BOTH, expand=True)

        self._render_ll_visual()

    def _render_ll_visual(self):
        for widget in self.ll_canvas.winfo_children():
            widget.destroy()

        items = self.demo_ll.to_list()
        count = len(items)

        tk.Label(self.ll_canvas, text=f"DOUBLY LINKED CHAIN (Total Nodes: {count})", font=FONTS["small"], fg="#94A3B8", bg="#0F172A").pack(anchor="w", pady=(0, 10))

        if count == 0:
            tk.Label(self.ll_canvas, text="[ Doubly Linked List is Empty : HEAD -> NULL ]", font=FONTS["body"], fg="#F59E0B", bg="#0F172A").pack(pady=40)
            return

        # Diagram frame
        diagram_box = tk.Frame(self.ll_canvas, bg="#0F172A")
        diagram_box.pack(fill=tk.X, pady=10)

        tk.Label(diagram_box, text="HEAD ➔", font=FONTS["body_bold"], fg="#38BDF8", bg="#0F172A").pack(side=tk.LEFT, padx=(0, 4))

        for idx, item in enumerate(items):
            node_frame = tk.Frame(diagram_box, bg="#1E293B", padx=8, pady=6, highlightbackground="#38BDF8", highlightthickness=1)
            node_frame.pack(side=tk.LEFT, padx=3)

            tk.Label(node_frame, text=f"[Node {idx + 1}]", font=FONTS["small"], fg="#A78BFA", bg="#1E293B").pack()
            # truncate text for compact display
            disp = item if len(item) <= 22 else item[:20] + ".."
            tk.Label(node_frame, text=disp, font=FONTS["code"], fg="#FFFFFF", bg="#1E293B").pack()

            if idx < count - 1:
                tk.Label(diagram_box, text="⇄", font=("Segoe UI", 14, "bold"), fg="#34D399", bg="#0F172A").pack(side=tk.LEFT, padx=2)

        tk.Label(diagram_box, text="➔ TAIL ➔ NULL", font=FONTS["body_bold"], fg="#38BDF8", bg="#0F172A").pack(side=tk.LEFT, padx=(4, 0))

    def _ll_insert_front(self):
        val = self.ll_input.get().strip()
        if not val:
            return
        self.demo_ll.insert_front(val)
        self.ll_status_lbl.config(text=f"✅ Inserted at HEAD in O(1) time: '{val}'", fg=PALETTE["success"])
        self._render_ll_visual()

    def _ll_insert_end(self):
        val = self.ll_input.get().strip()
        if not val:
            return
        self.demo_ll.insert_end(val)
        self.ll_status_lbl.config(text=f"✅ Appended at TAIL in O(1) time: '{val}'", fg=PALETTE["success"])
        self._render_ll_visual()

    def _ll_traverse(self):
        items = self.demo_ll.to_list()
        msg = f"Forward Traversal ({len(items)} nodes):\n\n" + "\n".join([f"Node {i+1}: {item}" for i, item in enumerate(items)])
        messagebox.showinfo("Linked List Traversal", msg)

    def _ll_clear(self):
        self.demo_ll.clear()
        self.ll_status_lbl.config(text="Linked list cleared.", fg=PALETTE["text_secondary"])
        self._render_ll_visual()

    # ==========================================
    # Tab 4: Searching Benchmark
    # ==========================================
    def _build_search_tab(self):
        top_bar = tk.Frame(self.tab_search, bg=PALETTE["bg_card"])
        top_bar.pack(fill=tk.X, pady=(0, 15))

        info_box = tk.Frame(top_bar, bg="#F3E8FF", padx=12, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(fill=tk.X)

        tk.Label(info_box, text="Comparative Complexity: Linear Search O(n) vs. Binary Search O(log2 n)", font=FONTS["body_bold"], fg="#7E22CE", bg="#F3E8FF").pack(anchor="w")
        tk.Label(info_box, text="Evaluates comparison telemetry on 25 sorted student roll numbers from database.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F3E8FF").pack(anchor="w")

        # Search query row
        query_bar = tk.Frame(self.tab_search, bg=PALETTE["bg_card"])
        query_bar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(query_bar, text="Target Roll Number:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 8))
        self.search_roll_var = tk.StringVar(value="EX105")
        self.search_entry = ttk.Entry(query_bar, textvariable=self.search_roll_var, font=FONTS["body"], width=15)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(query_bar, text="Execute Comparative Search Benchmark 🚀", style="Primary.TButton", command=self._run_search_benchmark).pack(side=tk.LEFT)

        # Result Cards Container
        self.search_res_frame = tk.Frame(self.tab_search, bg=PALETTE["bg_card"])
        self.search_res_frame.pack(fill=tk.BOTH, expand=True)

        self._run_search_benchmark()

    def _run_search_benchmark(self):
        for w in self.search_res_frame.winfo_children():
            w.destroy()

        target = self.search_roll_var.get().strip().upper()
        if not target:
            return

        # Fetch student roll numbers
        students = self.student_svc.get_all_students()
        # Sort roll numbers
        sorted_students = sorted(students, key=lambda s: s["roll_no"])
        roll_list = [s["roll_no"] for s in sorted_students]

        # Linear search
        lin_res, lin_comps = linear_search(roll_list, target)

        # Binary search
        bin_res, bin_comps = binary_search(roll_list, target)

        # Render Comparison Cards
        cards_row = tk.Frame(self.search_res_frame, bg=PALETTE["bg_card"])
        cards_row.pack(fill=tk.X, pady=(0, 15))

        # Card 1: Linear Search
        c1 = tk.Frame(cards_row, bg="#FEF2F2", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(c1, text="Linear Search O(n)", font=FONTS["heading"], fg=PALETTE["danger"], bg="#FEF2F2").pack(anchor="w")
        tk.Label(c1, text=f"Comparisons: {lin_comps}", font=FONTS["metric_value"], fg=PALETTE["danger"], bg="#FEF2F2").pack(anchor="w")
        status_lin = f"Target Found at Index {lin_res}" if lin_res is not None else "Target Not Found (404)"
        tk.Label(c1, text=f"Result: {status_lin}", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#FEF2F2").pack(anchor="w", pady=(4, 0))
        tk.Label(c1, text="Strategy: Sequential element-by-element scan.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#FEF2F2").pack(anchor="w")

        # Card 2: Binary Search
        c2 = tk.Frame(cards_row, bg="#ECFDF5", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        c2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(c2, text="Binary Search O(log2 n)", font=FONTS["heading"], fg=PALETTE["success"], bg="#ECFDF5").pack(anchor="w")
        tk.Label(c2, text=f"Comparisons: {bin_comps}", font=FONTS["metric_value"], fg=PALETTE["success"], bg="#ECFDF5").pack(anchor="w")
        status_bin = f"Target Found at Index {bin_res}" if bin_res is not None else "Target Not Found (404)"
        tk.Label(c2, text=f"Result: {status_bin}", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#ECFDF5").pack(anchor="w", pady=(4, 0))
        tk.Label(c2, text="Strategy: Divide-and-conquer interval halving.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#ECFDF5").pack(anchor="w")

        # Card 3: Speedup Telemetry
        c3 = tk.Frame(cards_row, bg="#EEF2FF", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        c3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        speedup = round(lin_comps / max(1, bin_comps), 2)
        tk.Label(c3, text="Algorithmic Advantage", font=FONTS["heading"], fg=PALETTE["primary"], bg="#EEF2FF").pack(anchor="w")
        tk.Label(c3, text=f"{speedup}x Fewer Checks", font=FONTS["metric_value"], fg=PALETTE["primary"], bg="#EEF2FF").pack(anchor="w")
        tk.Label(c3, text=f"Linear: {lin_comps} steps vs Binary: {bin_comps} steps", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#EEF2FF").pack(anchor="w", pady=(4, 0))
        tk.Label(c3, text="Demonstrates theoretical upper bounds in practice.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#EEF2FF").pack(anchor="w")

        # Array Preview Box
        arr_card = tk.Frame(self.search_res_frame, bg="#0F172A", padx=12, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        arr_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(arr_card, text="SORTED ARRAY UNDER TEST (Roll Numbers):", font=FONTS["small"], fg="#94A3B8", bg="#0F172A").pack(anchor="w")

        roll_preview = " | ".join([f"[{i}]: {r}" for i, r in enumerate(roll_list)])
        roll_lbl = tk.Label(arr_card, text=roll_preview, font=FONTS["code"], fg="#38BDF8", bg="#0F172A", wraplength=850, justify="left")
        roll_lbl.pack(anchor="w", pady=(6, 0))

    # ==========================================
    # Tab 5: Sorting Benchmark
    # ==========================================
    def _build_sort_tab(self):
        top_bar = tk.Frame(self.tab_sort, bg=PALETTE["bg_card"])
        top_bar.pack(fill=tk.X, pady=(0, 15))

        info_box = tk.Frame(top_bar, bg="#FFFBEB", padx=12, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(fill=tk.X)

        tk.Label(info_box, text="Sorting Algorithm Verification: Bubble Sort O(n^2), Selection Sort O(n^2), Merge Sort O(n log n)", font=FONTS["body_bold"], fg="#D97706", bg="#FFFBEB").pack(anchor="w")
        tk.Label(info_box, text="Validates asymptotic bounds, stability, comparison counts, and data-movement telemetry.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#FFFBEB").pack(anchor="w")

        # Controls
        ctrl_frame = tk.Frame(self.tab_sort, bg=PALETTE["bg_card"])
        ctrl_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(ctrl_frame, text="Sort By Attribute:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))
        self.sort_attr_var = tk.StringVar(value="name")
        attr_cb = ttk.Combobox(ctrl_frame, textvariable=self.sort_attr_var, values=["name", "roll_no", "admission_year"], state="readonly", width=16)
        attr_cb.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(ctrl_frame, text="Order:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))
        self.sort_order_var = tk.StringVar(value="Ascending")
        order_cb = ttk.Combobox(ctrl_frame, textvariable=self.sort_order_var, values=["Ascending", "Descending"], state="readonly", width=14)
        order_cb.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(ctrl_frame, text="Run Tri-Sort Benchmark ⚡", style="Primary.TButton", command=self._run_sort_benchmark).pack(side=tk.LEFT)

        # Benchmark Table
        table_frame = tk.Frame(self.tab_sort, bg=PALETTE["bg_card"])
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("algo", "time_avg", "space", "stable", "comps", "swaps", "equivalence")
        self.sort_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=4)
        self.sort_tree.heading("algo", text="Algorithm")
        self.sort_tree.heading("time_avg", text="Time (Average)")
        self.sort_tree.heading("space", text="Auxiliary Space")
        self.sort_tree.heading("stable", text="Stable?")
        self.sort_tree.heading("comps", text="Comparisons")
        self.sort_tree.heading("swaps", text="Swaps / Movements")
        self.sort_tree.heading("equivalence", text="Verification Output")

        self.sort_tree.column("algo", width=140, anchor="w")
        self.sort_tree.column("time_avg", width=120, anchor="center")
        self.sort_tree.column("space", width=100, anchor="center")
        self.sort_tree.column("stable", width=90, anchor="center")
        self.sort_tree.column("comps", width=120, anchor="center")
        self.sort_tree.column("swaps", width=140, anchor="center")
        self.sort_tree.column("equivalence", width=220, anchor="w")

        self.sort_tree.pack(fill=tk.X, pady=(0, 10))

        # Sorted Sample Display
        self.sort_preview_lbl = tk.Label(self.tab_sort, text="", font=FONTS["code"], fg=PALETTE["primary"], bg=PALETTE["bg_card"], justify="left", wraplength=850)
        self.sort_preview_lbl.pack(anchor="w")

        self._run_sort_benchmark()

    def _run_sort_benchmark(self):
        for item in self.sort_tree.get_children():
            self.sort_tree.delete(item)

        attr = self.sort_attr_var.get()
        reverse = (self.sort_order_var.get() == "Descending")

        students = self.student_svc.get_all_students()
        dataset = [dict(s) for s in students]

        key_func = lambda x: x.get(attr, "")

        # 1. Bubble Sort
        b_sorted, b_comps = bubble_sort([dict(d) for d in dataset], key_func=key_func, reverse=reverse)

        # 2. Selection Sort
        s_sorted, s_comps = selection_sort([dict(d) for d in dataset], key_func=key_func, reverse=reverse)

        # 3. Merge Sort
        m_sorted, m_comps = merge_sort([dict(d) for d in dataset], key_func=key_func, reverse=reverse)

        # Check equivalence
        b_keys = [key_func(x) for x in b_sorted]
        s_keys = [key_func(x) for x in s_sorted]
        m_keys = [key_func(x) for x in m_sorted]

        equiv = (b_keys == s_keys == m_keys)
        equiv_text = "✅ 100% Identical Output" if equiv else "Mismatch"

        self.sort_tree.insert("", tk.END, values=("Bubble Sort", "O(n²)", "O(1)", "Yes (Stable)", b_comps, f"In-place (≤ {b_comps})", equiv_text))
        self.sort_tree.insert("", tk.END, values=("Selection Sort", "O(n²)", "O(1)", "No (Unstable)", s_comps, f"In-place (≤ {len(dataset)})", equiv_text))
        self.sort_tree.insert("", tk.END, values=("Merge Sort", "O(n log n)", "O(n)", "Yes (Stable)", m_comps, f"{m_comps} merge moves", equiv_text))

        preview_vals = [f"{x.get('roll_no')}: {x.get('name')}" for x in m_sorted[:6]]
        self.sort_preview_lbl.config(
            text=f"Sample Sorted Output (Top 6 Elements):\n" + "  ➔  ".join(preview_vals) + ("..." if len(m_sorted) > 6 else "")
        )
