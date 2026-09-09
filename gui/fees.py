"""
Fee Management Screen for College Management System.
Features student fee ledger, balance reconciliation, payment recording, and receipts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Optional

from gui.styles import PALETTE, FONTS
from services.fee_service import FeeService
from utils.helpers import format_currency
from utils.export import export_fees_to_csv


class FeesScreen(tk.Frame):
    """
    Fees management and collection screen.
    """

    def __init__(self, parent, fee_service: FeeService, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.svc = fee_service
        self.db_path = db_path
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)
        tk.Label(title_box, text="Fee Ledger & Revenue Collection", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(anchor="w")
        tk.Label(title_box, text="Manage student tuition installments, balance reconciliation, and receipts", font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]).pack(anchor="w")

        btn_box = tk.Frame(header, bg=PALETTE["bg_main"])
        btn_box.pack(side=tk.RIGHT)
        ttk.Button(btn_box, text="⬇ Export CSV", style="Secondary.TButton", command=self.handle_export).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="💳 Record Payment", style="Primary.TButton", command=self.open_payment_dialog).pack(side=tk.LEFT, padx=4)

        # KPI Summary Cards Row
        kpi_row = tk.Frame(self, bg=PALETTE["bg_main"])
        kpi_row.pack(fill=tk.X, padx=20, pady=10)

        self.card_total = self._create_kpi_card(kpi_row, "Total Invoiced", "₹0.00", PALETTE["primary"])
        self.card_collected = self._create_kpi_card(kpi_row, "Collected Funds", "₹0.00", PALETTE["success"])
        self.card_pending = self._create_kpi_card(kpi_row, "Outstanding Dues", "₹0.00", PALETTE["danger"])

        # Filter & Table Card
        table_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        table_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        filter_row = tk.Frame(table_card, bg=PALETTE["bg_card"])
        filter_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_row, text="Status Filter:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="All Statuses")
        self.status_cb = ttk.Combobox(filter_row, textvariable=self.status_var, values=["All Statuses", "Paid", "Partial", "Pending"], state="readonly", width=16)
        self.status_cb.pack(side=tk.LEFT, padx=(0, 15))
        self.status_cb.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        ttk.Button(filter_row, text="Refresh", style="Secondary.TButton", command=self.load_data).pack(side=tk.RIGHT)

        cols = ("fee_id", "roll_no", "name", "dept", "total", "paid", "pending", "date", "status")
        self.tree = ttk.Treeview(table_card, columns=cols, show="headings")

        self.tree.heading("fee_id", text="Invoice #")
        self.tree.heading("roll_no", text="Roll No")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("dept", text="Department")
        self.tree.heading("total", text="Total Fee")
        self.tree.heading("paid", text="Paid Amount")
        self.tree.heading("pending", text="Pending Balance")
        self.tree.heading("date", text="Last Payment")
        self.tree.heading("status", text="Status")

        self.tree.column("fee_id", width=60, anchor="center")
        self.tree.column("roll_no", width=80, anchor="center")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("dept", width=160, anchor="w")
        self.tree.column("total", width=110, anchor="e")
        self.tree.column("paid", width=110, anchor="e")
        self.tree.column("pending", width=110, anchor="e")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        v_scroll = ttk.Scrollbar(table_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_kpi_card(self, parent, title: str, val: str, color: str) -> tk.Label:
        card = tk.Frame(parent, bg=PALETTE["bg_card"], padx=18, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        tk.Label(card, text=title, font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_card"]).pack(anchor="w")
        val_lbl = tk.Label(card, text=val, font=FONTS["subtitle"], fg=color, bg=PALETTE["bg_card"])
        val_lbl.pack(anchor="w", pady=(2, 0))
        return val_lbl

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        st = self.status_var.get()
        filter_st = None if st == "All Statuses" else st

        fees = self.svc.get_all_fees(status=filter_st)
        for f in fees:
            self.tree.insert("", tk.END, iid=str(f["fee_id"]), values=(
                f"INV-{f['fee_id']}",
                f["roll_no"],
                f["student_name"],
                f["department_name"],
                format_currency(f["total_fee"]),
                format_currency(f["paid_amount"]),
                format_currency(f["pending_amount"]),
                f["payment_date"] or "N/A",
                f["status"]
            ))

        # Update KPI Cards
        kpi = self.svc.get_financial_kpi_summary()
        self.card_total.config(text=format_currency(kpi["total_fee_amount"]))
        self.card_collected.config(text=format_currency(kpi["total_paid_amount"]))
        self.card_pending.config(text=format_currency(kpi["total_pending_amount"]))

    def open_payment_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student fee record from the table to record a payment.")
            return

        fee_id = int(selected[0])
        fees = self.svc.get_all_fees()
        rec = next((f for f in fees if f["fee_id"] == fee_id), None)
        if not rec:
            return

        if rec["pending_amount"] <= 0:
            messagebox.showinfo("Fully Paid", f"Student {rec['student_name']} has already cleared all dues!")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Record Fee Payment — {rec['student_name']}")
        dialog.geometry("420x340")
        dialog.transient(self)
        dialog.grab_set()

        form = tk.Frame(dialog, padx=20, pady=20, bg=PALETTE["bg_card"])
        form.pack(fill=tk.BOTH, expand=True)

        tk.Label(form, text="Fee Payment Processing", font=FONTS["subtitle"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 10))

        info_box = tk.Frame(form, bg="#F8FAFC", padx=10, pady=8, highlightbackground=PALETTE["border"], highlightthickness=1)
        info_box.pack(fill=tk.X, pady=(0, 12))
        tk.Label(info_box, text=f"Student: {rec['student_name']} ({rec['roll_no']})", font=FONTS["body_bold"], bg="#F8FAFC").pack(anchor="w")
        tk.Label(info_box, text=f"Outstanding Pending Balance: {format_currency(rec['pending_amount'])}", font=FONTS["small"], fg=PALETTE["danger"], bg="#F8FAFC").pack(anchor="w")

        tk.Label(form, text="Payment Amount (INR):", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        amt_ent = ttk.Entry(form)
        amt_ent.insert(0, str(rec["pending_amount"]))
        amt_ent.pack(fill=tk.X, pady=(2, 10))

        tk.Label(form, text="Payment Date (YYYY-MM-DD):", font=FONTS["small"], bg=PALETTE["bg_card"]).pack(anchor="w")
        date_ent = ttk.Entry(form)
        date_ent.insert(0, datetime.date.today().isoformat())
        date_ent.pack(fill=tk.X, pady=(2, 12))

        err_lbl = tk.Label(form, text="", font=FONTS["small"], fg=PALETTE["danger"], bg=PALETTE["bg_card"])
        err_lbl.pack(fill=tk.X, pady=(0, 8))

        def process():
            try:
                amt = float(amt_ent.get().strip())
                d_str = date_ent.get().strip()
                res = self.svc.record_payment(fee_id, amt, d_str)
                dialog.destroy()
                self.load_data()
                messagebox.showinfo("Receipt Confirmed", f"Recorded payment of {format_currency(amt)} successfully!\nRemaining Dues: {format_currency(res['pending_amount'])}")
            except Exception as e:
                err_lbl.config(text=str(e))

        btn_row = tk.Frame(form, bg=PALETTE["bg_card"])
        btn_row.pack(fill=tk.X)
        ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_row, text="Process Payment", style="Primary.TButton", command=process).pack(side=tk.RIGHT)

    def handle_export(self):
        import os
        export_path = os.path.join(os.getcwd(), "fees_export.csv")
        try:
            count = export_fees_to_csv(export_path, db_path=self.db_path)
            messagebox.showinfo("Export Successful", f"Exported {count} fee ledger records to:\n{export_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
