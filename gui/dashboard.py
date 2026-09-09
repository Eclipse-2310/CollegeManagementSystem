"""
Main Application Dashboard and Window Shell for College Management System.
Features:
1. Modern sidebar navigation with role-based access filtering.
2. Dynamic view routing between all academic and administrative screens.
3. Live Overview Screen with KPI metric cards, embedded native Canvas charts,
   and recent notice announcements.
4. Active user session badge and clean sign-out transition.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Callable, Dict, List, Optional
import datetime

from gui.styles import PALETTE, FONTS, configure_ttk_styles
from gui.canvas_charts import BarChart, DonutChart
from models.user import User

# Service Imports
from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.marks_service import MarksService
from services.fee_service import FeeService
from services.admin_service import AdminService
from services.library_service import LibraryService

# Screen Imports
from gui.students import StudentsScreen
from gui.faculty import FacultyScreen
from gui.attendance import AttendanceScreen
from gui.exams import ExamsScreen
from gui.timetable import TimetableScreen
from gui.fees import FeesScreen
from gui.library import LibraryScreen
from gui.notices import NoticesScreen
from gui.reports import ReportsScreen
from gui.ai_agent_screen import AIAgentScreen
from gui.dsa_demo import DSADemoScreen
from gui.dbms_demo import DBMSDemoScreen
from gui.settings import SettingsScreen
from database.database import DEFAULT_DB_PATH, fetch_all, fetch_one


class DashboardOverviewFrame(tk.Frame):
    """
    Landing Overview Screen displaying live KPI cards, Canvas charts,
    and recent announcements.
    """

    def __init__(self, parent, user: User, nav_callback: Callable[[str], None], db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.user = user
        self.nav_callback = nav_callback
        self.db_path = db_path or DEFAULT_DB_PATH

        self.student_svc = StudentService(db_path=self.db_path)
        self.attendance_svc = AttendanceService(db_path=self.db_path)
        self.fee_svc = FeeService(db_path=self.db_path)
        self.admin_svc = AdminService(db_path=self.db_path)
        self.library_svc = LibraryService(db_path=self.db_path)

        self._build_ui()
        self.refresh_metrics()

    def _build_ui(self):
        # Header Greeting
        top_banner = tk.Frame(self, bg=PALETTE["bg_main"])
        top_banner.pack(fill=tk.X, padx=20, pady=(15, 10))

        greet_box = tk.Frame(top_banner, bg=PALETTE["bg_main"])
        greet_box.pack(side=tk.LEFT)

        role_titles = {
            "Admin": "System Administrator",
            "Faculty": "Faculty Member",
            "Student": "Student Scholar"
        }
        role_label = role_titles.get(self.user.role, self.user.role)

        tk.Label(greet_box, text=f"Welcome back, {self.user.username} 👋", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(greet_box, text=f"Institutional Overview  |  Access Level: {role_label}", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w", pady=(2, 0))

        # Academic Term Tag
        term_tag = tk.Label(top_banner, text="ACADEMIC YEAR 2026-27 (TERM 1)", font=FONTS["small"], fg=PALETTE["primary"], bg=PALETTE["primary_light"], padx=10, pady=5)
        term_tag.pack(side=tk.RIGHT)

        # Metric KPI Cards Row
        kpi_row = tk.Frame(self, bg=PALETTE["bg_main"])
        kpi_row.pack(fill=tk.X, padx=20, pady=(0, 15))

        self.kpi_labels: Dict[str, tk.Label] = {}

        metrics_def = [
            ("students", "Total Students", "#EEF2FF", PALETTE["primary"]),
            ("faculty", "Faculty Members", "#F0FDF4", PALETTE["success"]),
            ("attendance_risk", "Attendance <75%", "#FEF2F2", PALETTE["danger"]),
            ("fee_recovery", "Fee Realization", "#FFFBEB", "#D97706"),
            ("notices_count", "Campus Notices", "#F3E8FF", "#7E22CE")
        ]

        for key, title, bg_col, fg_col in metrics_def:
            card = tk.Frame(kpi_row, bg=PALETTE["bg_card"], padx=14, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            # Icon/accent bar
            tk.Frame(card, bg=fg_col, height=3).pack(fill=tk.X, pady=(0, 8))

            val_lbl = tk.Label(card, text="--", font=FONTS["metric_value"], fg=fg_col, bg=PALETTE["bg_card"])
            val_lbl.pack(anchor="w")

            tk.Label(card, text=title, font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(anchor="w")
            self.kpi_labels[key] = val_lbl

        # Main Split Content: Left (Canvas Charts) | Right (Recent Notices & Actions)
        content_split = tk.Frame(self, bg=PALETTE["bg_main"])
        content_split.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        # Left Column: Canvas Charts (Width 60%)
        charts_col = tk.Frame(content_split, bg=PALETTE["bg_main"])
        charts_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Chart Card 1: Students by Course
        c1_card = tk.Frame(charts_col, bg=PALETTE["bg_card"], padx=12, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        c1_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.course_bar_chart = BarChart(c1_card, title="Student Enrollment Distribution by Course", width=520, height=210, bg=PALETTE["bg_card"])
        self.course_bar_chart.pack(fill=tk.BOTH, expand=True)

        # Chart Card 2: Fee Collection Breakdown
        c2_card = tk.Frame(charts_col, bg=PALETTE["bg_card"], padx=12, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        c2_card.pack(fill=tk.BOTH, expand=True)

        self.fee_donut_chart = DonutChart(c2_card, title="Fee Invoice Status Breakdown", width=520, height=210, bg=PALETTE["bg_card"])
        self.fee_donut_chart.pack(fill=tk.BOTH, expand=True)

        # Right Column: Announcements & Quick Missions (Width 40%)
        right_col = tk.Frame(content_split, bg=PALETTE["bg_main"], width=420)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_col.pack_propagate(False)

        # Announcements Card (Doubly Linked List real consumer)
        notices_card = tk.Frame(right_col, bg=PALETTE["bg_card"], padx=14, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        notices_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        n_top = tk.Frame(notices_card, bg=PALETTE["bg_card"])
        n_top.pack(fill=tk.X, pady=(0, 8))
        tk.Label(n_top, text="📢 Campus Notice Board", font=FONTS["heading"], fg=PALETTE["text_primary"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT)
        tk.Label(n_top, text="(Doubly Linked List)", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(side=tk.RIGHT)

        self.notices_box = tk.Frame(notices_card, bg=PALETTE["bg_card"])
        self.notices_box.pack(fill=tk.BOTH, expand=True)

        # Quick Actions Card
        action_card = tk.Frame(right_col, bg=PALETTE["bg_card"], padx=14, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        action_card.pack(fill=tk.X)

        tk.Label(action_card, text="⚡ Quick Shortcuts", font=FONTS["heading"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        actions = [
            ("🤖 Launch AI Campus Agent", "ai_agent", "#EEF2FF", PALETTE["primary"]),
            ("📋 Mark / View Attendance", "attendance", "#ECFDF5", PALETTE["success"]),
            ("🔬 Open DSA Viva Benchmark", "dsa_demo", "#FFFBEB", "#D97706"),
            ("🗄️ Open DBMS Viva Panel", "dbms_demo", "#F3E8FF", "#7E22CE")
        ]

        for lbl, screen_id, bg_col, fg_col in actions:
            tk.Button(
                action_card, text=lbl, font=FONTS["small"], bg=bg_col, fg=fg_col, relief="flat", padx=10, pady=6,
                cursor="hand2", anchor="w", command=lambda s=screen_id: self.nav_callback(s)
            ).pack(fill=tk.X, pady=2)

    def refresh_metrics(self):
        try:
            # 1. Total Students
            students = self.student_svc.get_all_students()
            self.kpi_labels["students"].config(text=str(len(students)))

            # 2. Faculty count
            fac_row = fetch_one("SELECT COUNT(*) AS count FROM faculty;", db_path=self.db_path)
            self.kpi_labels["faculty"].config(text=str(fac_row["count"] if fac_row else 0))

            # 3. Attendance Defaulters (<75%)
            defaulters = self.attendance_svc.get_defaulters_list()
            self.kpi_labels["attendance_risk"].config(text=f"{len(defaulters)} Defaulters")

            # 4. Fee Realization Rate
            fee_kpi = self.fee_svc.get_financial_kpi_summary()
            total_fee = fee_kpi.get("total_fee_amount", 0.0)
            paid_fee = fee_kpi.get("total_paid_amount", 0.0)
            pct = round((paid_fee / total_fee * 100), 1) if total_fee > 0 else 100.0
            self.kpi_labels["fee_recovery"].config(text=f"{pct}% Realized")

            # 5. Notices count
            notices = self.admin_svc.get_all_notices()
            self.kpi_labels["notices_count"].config(text=f"{len(notices)} Active")

            # 6. Render Bar Chart: Students by Course
            course_counts = fetch_all(
                """SELECT c.course_code, COUNT(s.student_id) AS cnt 
                   FROM courses c 
                   LEFT JOIN students s ON c.course_id = s.course_id 
                   GROUP BY c.course_id;""",
                db_path=self.db_path
            )
            bar_data = [(r["course_code"], float(r["cnt"])) for r in course_counts]
            if not bar_data:
                bar_data = [("BE-CE", 9.0), ("BE-IT", 8.0), ("BE-EXTC", 8.0)]
            self.course_bar_chart.draw_chart(bar_data, value_suffix=" Students")

            # 7. Render Donut Chart: Fee status breakdown
            fee_breakdown = fetch_all(
                "SELECT status, COUNT(*) AS cnt FROM fees GROUP BY status;",
                db_path=self.db_path
            )
            donut_data = [(r["status"], float(r["cnt"])) for r in fee_breakdown]
            if not donut_data:
                donut_data = [("Paid", 9.0), ("Partial", 8.0), ("Pending", 8.0)]
            self.fee_donut_chart.draw_chart(donut_data)

            # 8. Render Announcements list
            for w in self.notices_box.winfo_children():
                w.destroy()

            display_notices = notices[:4]
            if not display_notices:
                tk.Label(self.notices_box, text="No announcements posted yet.", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(pady=10)
            else:
                for n in display_notices:
                    n_row = tk.Frame(self.notices_box, bg="#F8FAFC", padx=8, pady=6, highlightbackground=PALETTE["border"], highlightthickness=1)
                    n_row.pack(fill=tk.X, pady=2)
                    tk.Label(n_row, text=f"📌 {n.title}", font=FONTS["body_bold"], fg=PALETTE["text_primary"], bg="#F8FAFC", anchor="w").pack(fill=tk.X)
                    sub_txt = f"By {n.posted_by} | {n.posted_date}"
                    tk.Label(n_row, text=sub_txt, font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F8FAFC", anchor="w").pack(fill=tk.X)

        except Exception as e:
            print(f"Error loading dashboard metrics: {e}")


class DashboardWindow:
    """
    Main Application Window Frame containing sidebar navigation,
    header session banner, and dynamic view routing container.
    """

    def __init__(self, root: tk.Tk, user: User, on_logout: Callable[[], None], db_path: Optional[str] = None):
        self.root = root
        self.user = user
        self.on_logout = on_logout
        self.db_path = db_path or DEFAULT_DB_PATH

        # Service instances shared across screens
        self.student_svc = StudentService(db_path=self.db_path)
        self.attendance_svc = AttendanceService(db_path=self.db_path)
        self.marks_svc = MarksService(db_path=self.db_path)
        self.fee_svc = FeeService(db_path=self.db_path)
        self.admin_svc = AdminService(db_path=self.db_path)
        self.library_svc = LibraryService(db_path=self.db_path)

        # Configure Root Window
        self.root.title(f"College Management System — Logged in as {self.user.username} ({self.user.role})")
        self.root.geometry("1320x800")
        self.root.minsize(1120, 680)

        # Track active navigation state
        self.current_screen_id: Optional[str] = None
        self.screen_instances: Dict[str, tk.Widget] = {}
        self.nav_buttons: Dict[str, tk.Button] = {}

        self._build_layout()
        self.switch_screen("dashboard")

    def _build_layout(self):
        # Outer shell
        self.shell = tk.Frame(self.root, bg=PALETTE["bg_main"])
        self.shell.pack(fill=tk.BOTH, expand=True)

        # 1. Left Sidebar (Fixed 240px)
        self.sidebar = tk.Frame(self.shell, bg=PALETTE["bg_sidebar"], width=240)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # 2. Main Content Area (Header + Screen Container)
        self.main_area = tk.Frame(self.shell, bg=PALETTE["bg_main"])
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_header()

        # Dynamic View Screen Container
        self.container = tk.Frame(self.main_area, bg=PALETTE["bg_main"])
        self.container.pack(fill=tk.BOTH, expand=True)

    def _build_sidebar(self):
        # Branding Logo
        brand_frame = tk.Frame(self.sidebar, bg=PALETTE["bg_sidebar"], pady=18, padx=16)
        brand_frame.pack(fill=tk.X)

        brand_top = tk.Frame(brand_frame, bg=PALETTE["bg_sidebar"])
        brand_top.pack(anchor="w")
        tk.Label(brand_top, text="🎓", font=("Segoe UI", 22), bg=PALETTE["bg_sidebar"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(brand_top, text="CAMPUS CMS", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg=PALETTE["bg_sidebar"]).pack(side=tk.LEFT)

        tk.Label(brand_frame, text="Academic ERP & Viva Suite", font=FONTS["small"], fg="#94A3B8", bg=PALETTE["bg_sidebar"]).pack(anchor="w", pady=(2, 0))

        # Divider
        tk.Frame(self.sidebar, height=1, bg="#1E293B").pack(fill=tk.X, padx=12, pady=(0, 8))

        # User Profile Box in Sidebar
        user_badge_frame = tk.Frame(self.sidebar, bg="#1E293B", padx=12, pady=10)
        user_badge_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        tk.Label(user_badge_frame, text=self.user.username, font=FONTS["body_bold"], fg="#FFFFFF", bg="#1E293B").pack(anchor="w")

        role_colors = {
            "Admin": ("#38BDF8", "#0369A1"),
            "Faculty": ("#34D399", "#047857"),
            "Student": ("#FBBF24", "#B45309")
        }
        role_fg, role_bg = role_colors.get(self.user.role, ("#FFFFFF", "#475569"))
        tk.Label(user_badge_frame, text=f"ROLE: {self.user.role.upper()}", font=("Segoe UI", 8, "bold"), fg=role_fg, bg="#1E293B").pack(anchor="w", pady=(2, 0))

        # Navigation Scroll Frame (to accommodate all 14 screens cleanly)
        nav_scroll_container = tk.Frame(self.sidebar, bg=PALETTE["bg_sidebar"])
        nav_scroll_container.pack(fill=tk.BOTH, expand=True)

        nav_canvas = tk.Canvas(nav_scroll_container, bg=PALETTE["bg_sidebar"], highlightthickness=0)
        nav_scrollbar = ttk.Scrollbar(nav_scroll_container, orient="vertical", command=nav_canvas.yview)
        self.nav_list_frame = tk.Frame(nav_canvas, bg=PALETTE["bg_sidebar"])

        self.nav_list_frame.bind(
            "<Configure>",
            lambda e: nav_canvas.configure(scrollregion=nav_canvas.bbox("all"))
        )
        nav_canvas.create_window((0, 0), window=self.nav_list_frame, anchor="nw", width=224)
        nav_canvas.configure(yscrollcommand=nav_scrollbar.set)

        nav_canvas.pack(side="left", fill="both", expand=True)
        # Only show scrollbar if list exceeds height
        nav_scrollbar.pack(side="right", fill="y")

        # Full Master Menu Registry
        all_menu_items = [
            ("dashboard", "📊 Dashboard", ["Admin", "Faculty", "Student"]),
            ("students", "👨‍🎓 Students", ["Admin"]),
            ("faculty", "👨‍🏫 Faculty", ["Admin"]),
            ("attendance", "📋 Attendance", ["Admin", "Faculty", "Student"]),
            ("exams", "📝 Exams & Marks", ["Admin", "Faculty", "Student"]),
            ("timetable", "📅 Timetable", ["Admin", "Faculty", "Student"]),
            ("fees", "💳 Fee Ledger", ["Admin", "Student"]),
            ("library", "📚 Library", ["Admin", "Student"]),
            ("notices", "📢 Notice Board", ["Admin", "Faculty", "Student"]),
            ("reports", "📈 Reports & Export", ["Admin", "Faculty"]),
            ("ai_agent", "🤖 AI Campus Agent", ["Admin", "Faculty"]),
            ("dsa_demo", "🔬 DSA Viva Panel", ["Admin", "Faculty"]),
            ("dbms_demo", "🗄️ DBMS Viva Panel", ["Admin", "Faculty"]),
            ("settings", "⚙️ System Settings", ["Admin", "Faculty", "Student"])
        ]

        # Filter items according to Role-Based Access Control (RBAC)
        for screen_id, label, allowed_roles in all_menu_items:
            if self.user.role in allowed_roles:
                btn = tk.Button(
                    self.nav_list_frame, text=f"  {label}", font=FONTS["sidebar_item"],
                    fg="#94A3B8", bg=PALETTE["bg_sidebar"], activebackground="#1E293B", activeforeground="#FFFFFF",
                    relief="flat", anchor="w", padx=14, pady=8, cursor="hand2",
                    command=lambda sid=screen_id: self.switch_screen(sid)
                )
                btn.pack(fill=tk.X, pady=1)
                self.nav_buttons[screen_id] = btn

        # Bottom Sign-Out Button
        signout_box = tk.Frame(self.sidebar, bg=PALETTE["bg_sidebar"], padx=12, pady=12)
        signout_box.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Button(
            signout_box, text="🚪 Sign Out", font=FONTS["body_bold"],
            fg="#EF4444", bg="#1E293B", activebackground="#EF4444", activeforeground="#FFFFFF",
            relief="flat", padx=10, pady=8, cursor="hand2", command=self.handle_sign_out
        ).pack(fill=tk.X)

    def _build_header(self):
        self.header_frame = tk.Frame(self.main_area, bg=PALETTE["bg_header"], height=52, padx=20, highlightbackground=PALETTE["border"], highlightthickness=1)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)

        self.header_title_lbl = tk.Label(self.header_frame, text="Dashboard Overview", font=FONTS["subtitle"], fg=PALETTE["text_primary"], bg=PALETTE["bg_header"])
        self.header_title_lbl.pack(side=tk.LEFT, pady=12)

        # Right Header Info
        header_right = tk.Frame(self.header_frame, bg=PALETTE["bg_header"])
        header_right.pack(side=tk.RIGHT, pady=12)

        today_str = datetime.date.today().strftime("%A, %d %B %Y")
        tk.Label(header_right, text=today_str, font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_header"]).pack(side=tk.LEFT, padx=(0, 15))

        status_dot = tk.Label(header_right, text="● SYSTEM LIVE", font=("Segoe UI", 8, "bold"), fg="#10B981", bg="#ECFDF5", padx=8, pady=3)
        status_dot.pack(side=tk.LEFT)

    def switch_screen(self, screen_id: str):
        """
        Switches the visible view in the container frame.
        Caches created screens for instant response.
        """
        if self.current_screen_id == screen_id and screen_id in self.screen_instances:
            return

        # Update button highlights
        for sid, btn in self.nav_buttons.items():
            if sid == screen_id:
                btn.config(bg=PALETTE["bg_sidebar_active"], fg="#38BDF8")
            else:
                btn.config(bg=PALETTE["bg_sidebar"], fg="#94A3B8")

        # Hide current screen
        for sc in self.screen_instances.values():
            sc.pack_forget()

        # Update Header Title
        title_mapping = {
            "dashboard": "Institutional Overview & Executive Summary",
            "students": "Student Enrollment & Records Management",
            "faculty": "Faculty Profiles & Department Allocation",
            "attendance": "Classroom Attendance Register & Defaulter Tracking",
            "exams": "Examinations & Marks Evaluation System",
            "timetable": "Master Weekly Timetable & Room Schedules",
            "fees": "Fee Invoices, Payment Tracking & Dues Ledger",
            "library": "Library Catalog & Circulation Desk",
            "notices": "Campus Notice Board & Announcements Chain",
            "reports": "Analytical Reports, Live Charts & CSV/JSON Export",
            "ai_agent": "Autonomous Campus Intelligence Agent (ReAct Cognitive Architecture)",
            "dsa_demo": "Data Structures & Algorithms Live Viva Evaluation Panel",
            "dbms_demo": "Database Management System (DBMS) Relational Schema & Constraints Lab",
            "settings": "System Settings, User Management & Database Maintenance"
        }
        self.header_title_lbl.config(text=title_mapping.get(screen_id, "College Management System"))

        # Instantiate or display screen
        if screen_id not in self.screen_instances:
            self.screen_instances[screen_id] = self._create_screen_instance(screen_id)

        target_screen = self.screen_instances[screen_id]
        target_screen.pack(fill=tk.BOTH, expand=True)
        self.current_screen_id = screen_id

        # Refresh overview if dashboard opened
        if screen_id == "dashboard" and isinstance(target_screen, DashboardOverviewFrame):
            target_screen.refresh_metrics()

    def _create_screen_instance(self, screen_id: str) -> tk.Widget:
        if screen_id == "dashboard":
            return DashboardOverviewFrame(self.container, self.user, nav_callback=self.switch_screen, db_path=self.db_path)
        elif screen_id == "students":
            return StudentsScreen(self.container, student_service=self.student_svc, db_path=self.db_path)
        elif screen_id == "faculty":
            return FacultyScreen(self.container, db_path=self.db_path)
        elif screen_id == "attendance":
            return AttendanceScreen(self.container, attendance_service=self.attendance_svc, db_path=self.db_path)
        elif screen_id == "exams":
            return ExamsScreen(self.container, marks_service=self.marks_svc, db_path=self.db_path)
        elif screen_id == "timetable":
            return TimetableScreen(self.container, admin_service=self.admin_svc, db_path=self.db_path)
        elif screen_id == "fees":
            return FeesScreen(self.container, fee_service=self.fee_svc, db_path=self.db_path)
        elif screen_id == "library":
            return LibraryScreen(self.container, library_service=self.library_svc, db_path=self.db_path)
        elif screen_id == "notices":
            return NoticesScreen(self.container, admin_service=self.admin_svc, db_path=self.db_path)
        elif screen_id == "reports":
            return ReportsScreen(self.container, db_path=self.db_path)
        elif screen_id == "ai_agent":
            return AIAgentScreen(self.container, db_path=self.db_path)
        elif screen_id == "dsa_demo":
            return DSADemoScreen(self.container, db_path=self.db_path)
        elif screen_id == "dbms_demo":
            return DBMSDemoScreen(self.container, db_path=self.db_path)
        elif screen_id == "settings":
            return SettingsScreen(self.container, db_path=self.db_path)
        else:
            fallback = tk.Frame(self.container, bg=PALETTE["bg_main"])
            tk.Label(fallback, text=f"Screen '{screen_id}' not found.", font=FONTS["title"]).pack(pady=40)
            return fallback

    def handle_sign_out(self):
        confirm = messagebox.askyesno("Confirm Sign Out", "Are you sure you want to sign out from the system?")
        if confirm:
            self.shell.destroy()
            self.on_logout()
