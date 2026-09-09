"""
Library Management Screen for College Management System.
Features Book Catalog, Borrowing/Return circulation, and FIFO Reservation Queue visualizer.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Optional

from gui.styles import PALETTE, FONTS
from services.library_service import LibraryService
from models.other_models import LibraryBook
from database.database import fetch_all


class LibraryScreen(tk.Frame):
    """
    Library catalog and FIFO request queue screen.
    """

    def __init__(self, parent, library_service: LibraryService, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.svc = library_service
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Library Catalog & Circulation", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text="Book inventory, student checkout circulation, and FIFO Reservation Queue", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="⚡ Queue Reservation (FIFO)", style="Secondary.TButton", command=self.open_queue_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="📖 Issue Book", style="Primary.TButton", command=self.open_issue_dialog).pack(side=tk.LEFT, padx=4)

        # Main Split: Left (Book Catalog) | Right (Active Queue)
        split = tk.Frame(self, bg=PALETTE["bg_main"])
        split.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left: Books Catalog
        left_card = tk.Frame(split, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Search Bar
        search_row = tk.Frame(left_card, bg=PALETTE["bg_card"])
        search_row.pack(fill=tk.X, pady=(0, 10))
        tk.Label(search_row, text="Search Titles:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_data())
        ttk.Entry(search_row, textvariable=self.search_var, width=24).pack(side=tk.LEFT)
        ttk.Button(search_row, text="Refresh", style="Secondary.TButton", command=self.load_data).pack(side=tk.RIGHT)

        # Table
        cols = ("id", "title", "author", "category", "isbn", "qty")
        self.tree = ttk.Treeview(left_card, columns=cols, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Book Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("category", text="Category")
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("qty", text="Copies")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("title", width=220, anchor="w")
        self.tree.column("author", width=150, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("isbn", width=120, anchor="center")
        self.tree.column("qty", width=60, anchor="center")

        v_scroll = ttk.Scrollbar(left_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Right: FIFO Reservation Queue Card
        right_card = tk.Frame(split, bg=PALETTE["bg_card"], width=320, padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_card.pack_propagate(False)

        tk.Label(right_card, text="Pending Requests (FIFO Queue)", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w")
        tk.Label(right_card, text="First-In First-Out waiting list for books", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        self.queue_box = tk.Listbox(right_card, font=FONTS["small"], bg="#F8FAFC", relief="flat", highlightbackground=PALETTE["border"], highlightthickness=1)
        self.queue_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Button(right_card, text="⚡ Process Next (Dequeue)", style="Primary.TButton", command=self.handle_process_queue).pack(fill=tk.X)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        search = self.search_var.get().strip() or None
        books = self.svc.get_all_books(search=search)

        for b in books:
            self.tree.insert("", tk.END, values=(
                b["book_id"],
                b["title"],
                b["author"],
                b["category"],
                b["isbn"],
                b["quantity"]
            ))

        # Refresh Queue Listbox
        self.queue_box.delete(0, tk.END)
        q_items = self.svc.request_queue.to_list()
        if not q_items:
            self.queue_box.insert(tk.END, "  (No pending requests in queue)")
        else:
            for idx, item in enumerate(q_items, 1):
                self.queue_box.insert(tk.END, f"{idx}. {item.request_id} — {item.requester_name}")
                self.queue_box.insert(tk.END, f"   {item.details[:35]}...")

    def open_issue_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Issue Library Book")
        dialog.geometry("420x280")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Book Checkout Transaction", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 15))

        books = fetch_all("SELECT book_id, title, quantity FROM library_books WHERE quantity > 0;", db_path=self.db_path)
        students = fetch_all("SELECT student_id, roll_no, name FROM students ORDER BY roll_no ASC;", db_path=self.db_path)

        b_opts = [f"{b['book_id']}: {b['title']} (Qty: {b['quantity']})" for b in books]
        s_opts = [f"{s['student_id']}: {s['roll_no']} - {s['name']}" for s in students]

        tk.Label(form, text="Select Book:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        b_combo = ttk.Combobox(form, values=b_opts, state="readonly")
        if b_opts:
            b_combo.current(0)
        b_combo.pack(fill=tk.X, pady=(2, 10))

        tk.Label(form, text="Select Student:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        s_combo = ttk.Combobox(form, values=s_opts, state="readonly")
        if s_opts:
            s_combo.current(0)
        s_combo.pack(fill=tk.X, pady=(2, 15))

        def issue():
            if not b_combo.get() or not s_combo.get():
                messagebox.showwarning("Incomplete", "Please select both book and student.")
                return
            b_id = int(b_combo.get().split(":")[0])
            s_id = int(s_combo.get().split(":")[0])
            try:
                self.svc.issue_book(b_id, s_id)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Success", "Book issued successfully. Available copies updated.")
            except Exception as e:
                messagebox.showerror("Issue Error", str(e))

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="Confirm Issue", style="Primary.TButton", command=issue).pack(side=tk.RIGHT)

    def open_queue_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Enqueue Book Reservation")
        dialog.geometry("400x240")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Add to FIFO Reservation Queue", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 12))

        tk.Label(form, text="Requester Name:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        name_ent = ttk.Entry(form)
        name_ent.insert(0, "Aarav Sharma")
        name_ent.pack(fill=tk.X, pady=(2, 8))

        tk.Label(form, text="Book Title / ISBN:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        isbn_ent = ttk.Entry(form)
        isbn_ent.insert(0, "978-0262033848 (CLRS)")
        isbn_ent.pack(fill=tk.X, pady=(2, 12))

        def enqueue():
            req_name = name_ent.get().strip()
            book_info = isbn_ent.get().strip()
            if req_name and book_info:
                req = self.svc.queue_issue_request(req_name, book_info)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Enqueued", f"Request {req.request_id} appended to FIFO Queue!")

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="Enqueue Request", style="Primary.TButton", command=enqueue).pack(side=tk.RIGHT)

    def handle_process_queue(self):
        req = self.svc.process_next_request()
        if req:
            self.load_data()
            messagebox.showinfo("Dequeued & Processed", f"FIFO Dequeue: Processed {req.request_id} for '{req.requester_name}'.")
        else:
            messagebox.showinfo("Empty Queue", "No pending requests in the FIFO queue.")
