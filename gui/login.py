"""
Login Dialog and Authentication Screen for College Management System.
Features a modern card aesthetic, error alerts, and one-click Role Switcher demo buttons.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from gui.styles import PALETTE, FONTS, configure_ttk_styles
from utils.security import authenticate_user, UserSession
from models.user import User


class LoginWindow:
    """
    Login Window presenting credentials input and demo role pre-fills.
    """

    def __init__(self, root: tk.Tk, on_login_success: Callable[[User], None], db_path: Optional[str] = None):
        self.root = root
        self.on_login_success = on_login_success
        self.db_path = db_path

        self.root.title("College Management System — Portal Sign In")
        self.root.geometry("460x560")
        self.root.resizable(False, False)

        # Center window on screen
        self._center_window(460, 560)
        configure_ttk_styles(self.root)

        self._build_ui()

    def _center_window(self, width: int, height: int):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        # Outer container frame
        main_frame = tk.Frame(self.root, bg=PALETTE["bg_main"], padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Inner Card
        card = tk.Frame(main_frame, bg=PALETTE["bg_card"], padx=25, pady=25, highlightbackground=PALETTE["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        # Header Badge & App Title
        tk.Label(card, text="🎓", font=("Segoe UI", 32), bg=PALETTE["bg_card"]).pack(pady=(0, 4))
        tk.Label(card, text="COLLEGE MANAGEMENT SYSTEM", font=("Segoe UI", 12, "bold"), fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack()
        tk.Label(card, text="Academic & Administration Portal", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(pady=(2, 16))

        # Divider
        tk.Frame(card, height=1, bg=PALETTE["border"]).pack(fill=tk.X, pady=(0, 16))

        # Username Input
        tk.Label(card, text="Username / Roll Number", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"], anchor="w").pack(fill=tk.X)
        self.username_var = tk.StringVar(value="admin")
        self.user_entry = ttk.Entry(card, textvariable=self.username_var, font=FONTS["body"])
        self.user_entry.pack(fill=tk.X, pady=(4, 12))

        # Password Input
        tk.Label(card, text="Password", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"], anchor="w").pack(fill=tk.X)
        self.password_var = tk.StringVar(value="admin123")
        self.pass_entry = ttk.Entry(card, textvariable=self.password_var, font=FONTS["body"], show="•")
        self.pass_entry.pack(fill=tk.X, pady=(4, 16))

        # Error Banner
        self.error_label = tk.Label(card, text="", font=FONTS["small"], fg=PALETTE["danger"], bg=PALETTE["bg_card"], wraplength=320)
        self.error_label.pack(fill=tk.X, pady=(0, 10))

        # Sign In Button
        sign_in_btn = ttk.Button(card, text="Sign In to System", style="Primary.TButton", command=self.handle_login)
        sign_in_btn.pack(fill=tk.X, pady=(0, 16))

        # One-Click Viva Demo Logins
        demo_box = tk.LabelFrame(card, text=" Quick Viva Evaluation Logins ", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"], padx=10, pady=10)
        demo_box.pack(fill=tk.X)

        btn_row = tk.Frame(demo_box, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)

        tk.Button(
            btn_row, text="Admin", font=FONTS["small"], bg="#EEF2FF", fg=PALETTE["primary"], relief="flat", padx=8, pady=4,
            command=lambda: self._set_credentials("admin", "admin123")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            btn_row, text="Faculty", font=FONTS["small"], bg="#ECFDF5", fg=PALETTE["success"], relief="flat", padx=8, pady=4,
            command=lambda: self._set_credentials("faculty1", "faculty123")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Button(
            btn_row, text="Student", font=FONTS["small"], bg="#FFFBEB", fg=PALETTE["warning"], relief="flat", padx=8, pady=4,
            command=lambda: self._set_credentials("student1", "student123")
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.handle_login())

    def _set_credentials(self, username: str, password: str):
        self.username_var.set(username)
        self.password_var.set(password)
        self.error_label.config(text="")

    def handle_login(self):
        u = self.username_var.get().strip()
        p = self.password_var.get()

        success, user_obj, message = authenticate_user(u, p, db_path=self.db_path)
        if success and user_obj:
            self.error_label.config(text="")
            self.on_login_success(user_obj)
        else:
            self.error_label.config(text=message)
