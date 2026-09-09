"""
Campus Notice Board Screen for College Management System.
Features chronological notice chain rendered directly via Doubly LinkedList data structure.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Optional

from gui.styles import PALETTE, FONTS
from services.admin_service import AdminService
from models.other_models import Notice


class NoticesScreen(tk.Frame):
    """
    Campus notices screen powered by Doubly LinkedList.
    """

    def __init__(self, parent, admin_service: AdminService, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.svc = admin_service
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Campus Notice Board (Doubly LinkedList Chain)", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text="Head points to latest notice; insert_front O(1) prepend; bidirectional node traversal", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="+ Publish Notice", style="Primary.TButton", command=self.open_publish_dialog).pack(side=tk.LEFT)

        # Main Split: Left (Interactive Linked List Visualizer Cards) | Right (Node Diagnostics)
        split = tk.Frame(self, bg=PALETTE["bg_main"])
        split.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left: Notices Scroll Canvas
        left_card = tk.Frame(split, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_card, text="Chronological Announcements", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        canvas_frame = tk.Frame(left_card, bg=PALETTE["bg_card"])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=PALETTE["bg_card"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.cards_container = tk.Frame(self.canvas, bg=PALETTE["bg_card"])

        self.cards_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Right: LinkedList Structure Inspection Card
        right_card = tk.Frame(split, bg=PALETTE["bg_card"], width=300, padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_card.pack_propagate(False)

        tk.Label(right_card, text="Data Structure Metadata", font=FONTS["subtitle"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        self.info_box = tk.Label(
            right_card, text="", font=FONTS["small"], bg="#F8FAFC", fg=PALETTE["text_secondary"],
            justify="left", anchor="nw", padx=10, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1
        )
        self.info_box.pack(fill=tk.BOTH, expand=True)

    def load_data(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        notices = self.svc.get_all_notices()
        size = self.svc.notice_chain.size()

        if not notices:
            tk.Label(self.cards_container, text="No campus announcements posted yet.", font=FONTS["body"], bg=PALETTE["bg_card"], fg=PALETTE["text_muted"]).pack(pady=30)
        else:
            for idx, n in enumerate(notices):
                # Notice card representing a node in the Doubly LinkedList
                card = tk.Frame(self.cards_container, bg="#F8FAFC", padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
                card.pack(fill=tk.X, expand=True, pady=6)

                top_bar = tk.Frame(card, bg="#F8FAFC")
                top_bar.pack(fill=tk.X)

                # Node indicator
                badge_text = "HEAD NODE [NEWEST]" if idx == 0 else f"NODE #{idx+1}"
                badge_color = PALETTE["primary"] if idx == 0 else PALETTE["text_secondary"]
                tk.Label(top_bar, text=badge_text, font=FONTS["small"], fg=badge_color, bg="#EEF2FF", padx=6, pady=2).pack(side=tk.LEFT)

                tk.Label(top_bar, text=f"Posted by: {n.posted_by} | {n.posted_date}", font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F8FAFC").pack(side=tk.RIGHT)

                # Title
                tk.Label(card, text=n.title, font=FONTS["subtitle"], fg=PALETTE["text_primary"], bg="#F8FAFC").pack(anchor="w", pady=(6, 4))
                # Description
                tk.Label(card, text=n.description, font=FONTS["body"], fg=PALETTE["text_primary"], bg="#F8FAFC", wraplength=480, justify="left").pack(anchor="w", pady=(0, 8))

                # Delete node button
                bot_bar = tk.Frame(card, bg="#F8FAFC")
                bot_bar.pack(fill=tk.X)
                tk.Button(
                    bot_bar, text="🗑 Delete Node", font=FONTS["small"], fg=PALETTE["danger"], bg="#F8FAFC", relief="flat", cursor="hand2",
                    command=lambda nid=n.notice_id: self.delete_notice(nid)
                ).pack(side=tk.RIGHT)

                if idx < len(notices) - 1:
                    tk.Label(self.cards_container, text="⇅ prev / next pointers ⇅", font=FONTS["small"], fg=PALETTE["text_muted"], bg=PALETTE["bg_card"]).pack(pady=1)

        # Update metadata info
        meta_text = (
            f"Structure: Doubly LinkedList\n\n"
            f"Total Nodes: {size}\n"
            f"Head Pointer: {'Active' if size > 0 else 'Null'}\n"
            f"Tail Pointer: {'Active' if size > 0 else 'Null'}\n\n"
            f"Asymptotic Complexity:\n"
            f"• Prepend (insert_front): O(1)\n"
            f"• Append (insert_rear): O(1)\n"
            f"• Delete node: O(n) scan + O(1) splice\n"
            f"• Sequential walk: O(n)\n\n"
            f"Evaluation Note:\n"
            f"Notices are stored as linked nodes so new announcements are prepended in O(1) without re-indexing array memory!"
        )
        self.info_box.config(text=meta_text)

    def open_publish_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Publish Campus Announcement")
        dialog.geometry("440x320")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="New Campus Notice (O(1) Prepend)", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 10))

        tk.Label(form, text="Notice Title:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        t_ent = ttk.Entry(form)
        t_ent.insert(0, "Upcoming Hackathon Registrations")
        t_ent.pack(fill=tk.X, pady=(2, 8))

        tk.Label(form, text="Announcement Body:", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        d_ent = ttk.Entry(form)
        d_ent.insert(0, "All engineering students can register teams on the student portal.")
        d_ent.pack(fill=tk.X, pady=(2, 8))

        tk.Label(form, text="Posted By (Authority):", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        p_ent = ttk.Entry(form)
        p_ent.insert(0, "Dean of Student Affairs")
        p_ent.pack(fill=tk.X, pady=(2, 12))

        def publish():
            title = t_ent.get().strip()
            desc = d_ent.get().strip()
            by = p_ent.get().strip()
            if title and desc and by:
                self.svc.publish_notice(title, desc, by)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Published", "Notice prepended to head of Doubly LinkedList!")

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="Publish to Chain", style="Primary.TButton", command=publish).pack(side=tk.RIGHT)

    def delete_notice(self, notice_id: int):
        confirm = messagebox.askyesno("Confirm Delete", "Remove this notice from database and unlink node?")
        if confirm:
            self.svc.delete_notice(notice_id)
            self.load_data()
