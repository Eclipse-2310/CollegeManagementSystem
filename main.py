"""
College Management System (CMS) - Main Entry Point.
Modular, academically strong desktop application for S.E. Engineering projects.
"""

import sys
import os
import tkinter as tk

# Ensure the root directory is on the sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import initialize_database, DEFAULT_DB_PATH
from gui.styles import configure_ttk_styles
from gui.login import LoginWindow
from gui.dashboard import DashboardWindow


def main():
    """Main application lifecycle controller."""
    # Ensure database tables, indexes, and seed records are initialized
    initialize_database(DEFAULT_DB_PATH)

    root = tk.Tk()
    configure_ttk_styles(root)

    def show_dashboard(user):
        for widget in root.winfo_children():
            widget.destroy()
        DashboardWindow(root, user=user, on_logout=show_login, db_path=DEFAULT_DB_PATH)

    def show_login():
        for widget in root.winfo_children():
            widget.destroy()
        LoginWindow(root, on_login_success=show_dashboard, db_path=DEFAULT_DB_PATH)

    show_login()
    root.mainloop()


if __name__ == "__main__":
    main()
