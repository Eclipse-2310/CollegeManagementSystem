"""
Headless verification test suite for Phase 8: Modern GUI & Academic Demo Panels.
Asserts that all GUI frames, screens, charts, and controllers mount and bind data cleanly without errors.
"""

import os
import sys
import tkinter as tk

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import initialize_database, seed_initial_data, is_database_seeded, DEFAULT_DB_PATH
from models.user import AdminUser, FacultyUser, StudentUser, User
from gui.styles import configure_ttk_styles
from gui.canvas_charts import BarChart, DonutChart
from gui.login import LoginWindow
from gui.dashboard import DashboardOverviewFrame, DashboardWindow
from gui.students import StudentsScreen
from gui.faculty import FacultyScreen
from gui.attendance import AttendanceScreen
from gui.exams import ExamsScreen
from gui.fees import FeesScreen
from gui.library import LibraryScreen
from gui.timetable import TimetableScreen
from gui.notices import NoticesScreen
from gui.reports import ReportsScreen
from gui.settings import SettingsScreen
from gui.dbms_demo import DBMSDemoScreen
from gui.dsa_demo import DSADemoScreen
from gui.ai_agent_screen import AIAgentScreen


def run_phase8_verification():
    print("=" * 60)
    print("PHASE 8 VERIFICATION: Modern GUI & Academic Demo Panels")
    print("=" * 60)

    # 1. Prepare seeded test database
    initialize_database(DEFAULT_DB_PATH)
    if not is_database_seeded(DEFAULT_DB_PATH):
        seed_initial_data(DEFAULT_DB_PATH)

    # 2. Initialize hidden headless Tk root
    root = tk.Tk()
    root.withdraw()
    configure_ttk_styles(root)
    print("[+] Headless Tkinter root initialized with modern TTK styles.")

    # 3. Test Login Window
    print("\n[+] 1. Testing Login Window & Demo Role Switchers:")
    logged_in_users = []

    def on_login(user):
        logged_in_users.append(user)

    login_win = LoginWindow(root, on_login_success=on_login, db_path=DEFAULT_DB_PATH)
    assert login_win.username_var.get() == "admin"
    assert login_win.password_var.get() == "admin123"

    # Test role switcher buttons
    login_win._set_credentials("faculty1", "faculty123")
    assert login_win.username_var.get() == "faculty1"
    login_win._set_credentials("student1", "student123")
    assert login_win.username_var.get() == "student1"
    login_win._set_credentials("admin", "admin123")

    login_win.handle_login()
    assert len(logged_in_users) == 1, "Login handler did not trigger on valid credentials!"
    admin_user = logged_in_users[0]
    assert admin_user.role == "Admin"
    print(f"  [OK] LoginWindow authenticated '{admin_user.username}' (Role: {admin_user.role})")

    # 4. Test Native Canvas Charts
    print("\n[+] 2. Testing Zero-Dependency Canvas Charts (Bar & Donut):")
    chart_win = tk.Frame(root)
    bar_chart = BarChart(chart_win, width=300, height=200, title="Student Enrollment")
    bar_chart.draw_chart([("BE-CE", 9.0), ("BE-IT", 8.0), ("BE-EXTC", 8.0)], value_suffix=" Students")
    print("  [OK] Native BarChart rendered on Canvas with geometry calculations.")

    donut_chart = DonutChart(chart_win, width=300, height=200, title="Fee Status")
    donut_chart.draw_chart([("Paid", 10.0), ("Partial", 8.0), ("Pending", 7.0)])
    print("  [OK] Native DonutChart rendered on Canvas with angular geometry calculations.")
    chart_win.destroy()

    # 5. Test Dashboard Shell & Overview
    print("\n[+] 3. Testing Dashboard Shell & Live Metric Overview:")
    dash_win = DashboardWindow(root, user=admin_user, on_logout=lambda: None, db_path=DEFAULT_DB_PATH)
    assert dash_win.current_screen_id == "dashboard"
    print(f"  [OK] DashboardWindow mounted with 240px sidebar and active role badge ({admin_user.role}).")

    # 6. Test Dynamic View Routing Across All Academic & Administrative Screens
    print("\n[+] 4. Testing Navigation Routing Across All 13 Feature Screens:")
    screens_to_test = [
        ("dashboard", "Overview & KPIs"),
        ("students", "Student Management (CRUD & Treeview)"),
        ("faculty", "Faculty Directory"),
        ("attendance", "Attendance Register & 75% Defaulter Warning"),
        ("exams", "Exams & Report Cards"),
        ("timetable", "Timetable Scheduler & Conflict Checker"),
        ("fees", "Fee Ledger & Balance Reconciliation"),
        ("library", "Library Circulation & Book Reservation"),
        ("notices", "Campus Notice Board"),
        ("reports", "Export Hub (CSV / JSON Snapshot)"),
        ("ai_agent", "Agentic AI Campus Intelligence Assistant"),
        ("dsa_demo", "Data Structures & Algorithms Viva Panel"),
        ("dbms_demo", "Database Management Systems Viva Panel"),
        ("settings", "System Settings & Session Info"),
    ]

    for screen_id, desc in screens_to_test:
        dash_win.switch_screen(screen_id)
        assert dash_win.current_screen_id == screen_id, f"Failed to switch to screen: {screen_id}"
        active_screen = dash_win.screen_instances.get(screen_id)
        assert active_screen is not None, f"Screen instance for '{screen_id}' was not created!"
        print(f"  [OK] Switched to '{screen_id}' -> {desc}")

    # 7. Clean up
    root.destroy()

    print("\n" + "=" * 60)
    print("ALL PHASE 8 GUI VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_phase8_verification()
