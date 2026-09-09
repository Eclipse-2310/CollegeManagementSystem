import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from gui.styles import PALETTE, FONTS
from gui.canvas_charts import BarChart, DonutChart
from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.fee_service import FeeService
from utils.export import export_students_csv, export_attendance_csv, export_fees_csv, export_full_backup_json
from database.database import fetch_all

class ReportsScreen(tk.Frame):
    def __init__(self, parent, db_path=None):
        super().__init__(parent, bg=PALETTE['bg_main'])
        self.db_path = db_path
        self.student_svc = StudentService(db_path=db_path)
        self.attendance_svc = AttendanceService(db_path=db_path)
        self.fee_svc = FeeService(db_path=db_path)
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=PALETTE['bg_main'])
        hdr.pack(fill=tk.X, padx=20, pady=(16, 8))
        tb = tk.Frame(hdr, bg=PALETTE['bg_main']); tb.pack(side=tk.LEFT)
        tk.Label(tb, text='Analytics and Reports', font=FONTS['title'], fg=PALETTE['text_primary'], bg=PALETTE['bg_main']).pack(anchor='w')
        tk.Label(tb, text='Live KPI Dashboards  |  CSV/JSON Export', font=FONTS['small'], fg=PALETTE['text_secondary'], bg=PALETTE['bg_main']).pack(anchor='w')
        eb = tk.Frame(hdr, bg=PALETTE['bg_main']); eb.pack(side=tk.RIGHT)
        for lbl, cmd in [('Students CSV', self._export_students), ('Attendance CSV', self._export_attendance), ('Fees CSV', self._export_fees), ('Backup JSON', self._export_backup)]:
            tk.Button(eb, text=lbl, font=FONTS['small'], bg=PALETTE['primary_light'], fg=PALETTE['primary'], relief='flat', padx=8, pady=5, cursor='hand2', command=cmd).pack(side=tk.LEFT, padx=3)
        kf = tk.Frame(self, bg=PALETTE['bg_main']); kf.pack(fill=tk.X, padx=20, pady=(0, 12))
        self.kpi_cards = {}
        for key, lbl, fg, bg in [('total_students','Total Students',PALETTE['primary'],'#EEF2FF'),('fee_collected','Fee Collected',PALETTE['success'],'#ECFDF5'),('att_defaulters','Att. Defaulters',PALETTE['danger'],'#FEF2F2'),('books_issued','Books Issued','#7C3AED','#F3E8FF')]:
            c = tk.Frame(kf, bg=bg, padx=18, pady=14, highlightbackground=PALETTE['border'], highlightthickness=1); c.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,10))
            v = tk.Label(c, text='-', font=FONTS['metric_value'], fg=fg, bg=bg); v.pack(anchor='w')
            tk.Label(c, text=lbl, font=FONTS['small'], fg=PALETTE['text_secondary'], bg=bg).pack(anchor='w')
            self.kpi_cards[key] = v
        cf = tk.Frame(self, bg=PALETTE['bg_main']); cf.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,16))
        fc = tk.Frame(cf, bg=PALETTE['bg_card'], highlightbackground=PALETTE['border'], highlightthickness=1); fc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        tk.Label(fc, text='Fee Collection Status', font=FONTS['subtitle'], fg=PALETTE['text_primary'], bg=PALETTE['bg_card']).pack(pady=(12,4))
        self.fee_donut = DonutChart(fc, width=280, height=200, bg=PALETTE['bg_card']); self.fee_donut.pack(pady=(4,12))
        ac = tk.Frame(cf, bg=PALETTE['bg_card'], highlightbackground=PALETTE['border'], highlightthickness=1); ac.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,10))
        tk.Label(ac, text='Students by Course', font=FONTS['subtitle'], fg=PALETTE['text_primary'], bg=PALETTE['bg_card']).pack(pady=(12,4))
        self.att_bar = BarChart(ac, width=360, height=200, bg=PALETTE['bg_card']); self.att_bar.pack(pady=(4,12))
        sc = tk.Frame(cf, bg=PALETTE['bg_card'], highlightbackground=PALETTE['border'], highlightthickness=1); sc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(sc, text='Enrollment Status', font=FONTS['subtitle'], fg=PALETTE['text_primary'], bg=PALETTE['bg_card']).pack(pady=(12,4))
        self.stu_donut = DonutChart(sc, width=280, height=200, bg=PALETTE['bg_card']); self.stu_donut.pack(pady=(4,12))
        btm = tk.Frame(self, bg=PALETTE['bg_main']); btm.pack(pady=(0,12))
        ttk.Button(btm, text='Refresh All Charts', style='Secondary.TButton', command=self._load_data).pack()

    def _load_data(self):
        try:
            students = self.student_svc.get_all_students()
            self.kpi_cards['total_students'].config(text=str(len(students)))
            fee_kpi = self.fee_svc.get_financial_kpi_summary()
            collected = fee_kpi.get('total_paid_amount', 0.0)
            self.kpi_cards['fee_collected'].config(text='Rs ' + '{:,.0f}'.format(collected))
            defaulters = self.attendance_svc.get_defaulters_list()
            self.kpi_cards['att_defaulters'].config(text=str(len(defaulters)))
            issued = fetch_all('SELECT COUNT(*) AS cnt FROM library_transactions WHERE return_date IS NULL;', db_path=self.db_path)
            self.kpi_cards['books_issued'].config(text=str(issued[0]['cnt'] if issued else 0))
            paid = fee_kpi.get('total_paid_amount', 0.0); pending = fee_kpi.get('total_pending_amount', 0.0)
            self.fee_donut.draw_chart([('Collected', paid), ('Pending', pending)] if (paid+pending)>0 else [('No Data', 1)], colors=[PALETTE['success'], PALETTE['danger']])
            rows = fetch_all('SELECT c.course_code, COUNT(s.student_id) AS n FROM courses c LEFT JOIN students s ON s.course_id=c.course_id GROUP BY c.course_id LIMIT 6;', db_path=self.db_path)
            self.att_bar.draw_chart([(r['course_code'], float(r['n'])) for r in rows] if rows else [('No Data', 0)], bar_color=PALETTE['secondary'])
            status_rows = fetch_all('SELECT status, COUNT(*) AS cnt FROM students GROUP BY status;', db_path=self.db_path)
            if status_rows:
                clrs = [PALETTE['success'], PALETTE['danger'], PALETTE['warning'], PALETTE['primary']]
                self.stu_donut.draw_chart([(r['status'].capitalize(), r['cnt']) for r in status_rows], colors=clrs[:len(status_rows)])
            else:
                self.stu_donut.draw_chart([('No Data', 1)])
        except Exception as exc:
            messagebox.showwarning('Reports', 'Chart load error: ' + str(exc))

    def _export_students(self):
        p = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')], initialfile='students_export.csv')
        if not p: return
        try: messagebox.showinfo('Export', 'Exported ' + str(export_students_csv(output_path=p, db_path=self.db_path)) + ' records.')
        except Exception as e: messagebox.showerror('Export Error', str(e))

    def _export_attendance(self):
        p = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')], initialfile='attendance_export.csv')
        if not p: return
        try: messagebox.showinfo('Export', 'Exported ' + str(export_attendance_csv(output_path=p, db_path=self.db_path)) + ' records.')
        except Exception as e: messagebox.showerror('Export Error', str(e))

    def _export_fees(self):
        p = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')], initialfile='fees_export.csv')
        if not p: return
        try: messagebox.showinfo('Export', 'Exported ' + str(export_fees_csv(output_path=p, db_path=self.db_path)) + ' records.')
        except Exception as e: messagebox.showerror('Export Error', str(e))

    def _export_backup(self):
        p = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')], initialfile='cms_backup.json')
        if not p: return
        try: export_full_backup_json(output_path=p, db_path=self.db_path); messagebox.showinfo('Backup', 'Backup exported.')
        except Exception as e: messagebox.showerror('Backup Error', str(e))