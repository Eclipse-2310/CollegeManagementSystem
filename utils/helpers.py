"""
Formatting, date utilities, and UI helper routines for College Management System.
"""

import datetime
from typing import Any, Optional


def format_currency(amount: float) -> str:
    """Format floating point amount into Indian Rupee format (e.g., ₹50,000.00)."""
    try:
        val = float(amount)
        return f"₹{val:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"


def format_percentage(pct: float) -> str:
    """Format percentage to 2 decimal places."""
    try:
        val = float(pct)
        return f"{val:.2f}%"
    except (ValueError, TypeError):
        return "0.00%"


def format_date_display(iso_date_str: Optional[str]) -> str:
    """Convert YYYY-MM-DD to DD-Mon-YYYY (e.g. 15-Sep-2026)."""
    if not iso_date_str:
        return "N/A"
    try:
        dt = datetime.date.fromisoformat(iso_date_str.strip())
        return dt.strftime("%d-%b-%Y")
    except Exception:
        return str(iso_date_str)


def get_status_color(status: str) -> str:
    """Return hex color code associated with business entity status."""
    st = str(status).strip().upper()
    mapping = {
        "PRESENT": "#10B981",    # Green
        "ABSENT": "#EF4444",     # Red
        "PAID": "#10B981",       # Green
        "PARTIAL": "#F59E0B",    # Amber
        "PENDING": "#EF4444",    # Red
        "ISSUED": "#3B82F6",     # Blue
        "RETURNED": "#10B981",   # Green
        "OVERDUE": "#EF4444",    # Red
        "PASS": "#10B981",       # Green
        "FAIL": "#EF4444"        # Red
    }
    return mapping.get(st, "#64748B")  # Slate fallback
