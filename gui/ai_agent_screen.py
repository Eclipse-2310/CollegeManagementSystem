"""
AI Agent Assistant Screen for College Management System.
Provides an interactive Autonomous Agent terminal demonstrating:
1. ReAct Cognitive Architecture (Reasoning -> Planning -> Tool Execution -> Reflection).
2. Autonomous Multi-Tool Orchestration over DB and Services.
3. Pre-configured Autonomous Campus Workflows.
4. Natural Language Institutional Question Answering.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Any, Dict, Optional

from gui.styles import PALETTE, FONTS
from services.ai_agent import CampusIntelligenceAgent


class AIAgentScreen(tk.Frame):
    """
    Autonomous AI Agent Screen demonstrating Agentic AI in College Management.
    """

    def __init__(self, parent, db_path: Optional[str] = None):
        super().__init__(parent, bg=PALETTE["bg_main"])
        self.db_path = db_path
        self.agent = CampusIntelligenceAgent(db_path=self.db_path)
        self._build_ui()

    def _build_ui(self):
        # Top Header Bar
        header = tk.Frame(self, bg=PALETTE["bg_main"], pady=8)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_box = tk.Frame(header, bg=PALETTE["bg_main"])
        title_box.pack(side=tk.LEFT)

        title_row = tk.Frame(title_box, bg=PALETTE["bg_main"])
        title_row.pack(anchor="w")
        tk.Label(title_row, text="🤖", font=("Segoe UI", 18), bg=PALETTE["bg_main"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(title_row, text="Autonomous Campus Intelligence Agent", font=FONTS["title"], fg=PALETTE["text_primary"], bg=PALETTE["bg_main"]).pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="ReAct Cognitive Cycle (Perception → Planning → Tool Calling → Reflection) over live College Database",
            font=FONTS["small"], fg=PALETTE["text_secondary"], bg=PALETTE["bg_main"]
        ).pack(anchor="w", pady=(2, 0))

        # Status badge
        status_badge = tk.Label(header, text="● AGENT ACTIVE & READY", font=FONTS["small"], fg="#059669", bg="#ECFDF5", padx=10, pady=5)
        status_badge.pack(side=tk.RIGHT)

        # Quick Autonomous Workflows Card
        workflows_card = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=12, highlightbackground=PALETTE["border"], highlightthickness=1)
        workflows_card.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(workflows_card, text="⚡ Autonomous Action Missions (1-Click Agent Execution):", font=FONTS["heading"], fg=PALETTE["primary"], bg=PALETTE["bg_card"]).pack(anchor="w", pady=(0, 8))

        wf_buttons = [
            ("📊 Campus Health Audit", "Give me an executive briefing on college performance and health", "#EEF2FF", PALETTE["primary"]),
            ("⚠️ Attendance Intervention", "Analyze students with attendance shortage below 75% and advise", "#FEF2F2", PALETTE["danger"]),
            ("💰 Financial Dues Audit", "Evaluate fee collections, outstanding dues, and revenue balance", "#FFFBEB", "#D97706"),
            ("🔍 Student 360 Diagnostic", "Inspect student profile CE101 across attendance, marks, fees", "#ECFDF5", PALETTE["success"]),
            ("📅 Timetable Clash Audit", "Check master timetable for double-booking overlaps", "#F3E8FF", "#7E22CE")
        ]

        btn_bar = tk.Frame(workflows_card, bg=PALETTE["bg_card"])
        btn_bar.pack(fill=tk.X)

        for label, query, bg_color, fg_color in wf_buttons:
            tk.Button(
                btn_bar, text=label, font=FONTS["small"], bg=bg_color, fg=fg_color, relief="flat", padx=10, pady=6,
                cursor="hand2", command=lambda q=query: self.dispatch_agent(q)
            ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

        # Main Split Frame: Left (Agent Terminal & Output) | Right (Thought & Tool Registry)
        split_frame = tk.Frame(self, bg=PALETTE["bg_main"])
        split_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        # Left Column: Agent Reasoning & Output Terminal
        left_card = tk.Frame(split_frame, bg=PALETTE["bg_card"], padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        left_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_card, text="Agent Dialogue & Synthesis Output", font=FONTS["subtitle"], bg=PALETTE["bg_card"], fg=PALETTE["text_primary"]).pack(anchor="w")

        # Terminal Output Box
        self.terminal = tk.Text(
            left_card, font=FONTS["code"], bg="#0F172A", fg="#F8FAFC",
            insertbackground="#FFFFFF", relief="flat", padx=12, pady=12, wrap=tk.WORD
        )
        term_scroll = ttk.Scrollbar(left_card, orient=tk.VERTICAL, command=self.terminal.yview)
        self.terminal.configure(yscrollcommand=term_scroll.set)

        self.terminal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(8, 0))
        term_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(8, 0))

        # Configure Terminal Color Tags
        self.terminal.tag_config("prompt", foreground="#38BDF8")      # Light blue
        self.terminal.tag_config("thought", foreground="#FBBF24")     # Yellow
        self.terminal.tag_config("tool", foreground="#A78BFA")        # Purple
        self.terminal.tag_config("result", foreground="#34D399")      # Green
        self.terminal.tag_config("error", foreground="#F87171")       # Red
        self.terminal.tag_config("divider", foreground="#475569")     # Slate

        # Right Column: Tool Registry & Agent Metadata
        right_card = tk.Frame(split_frame, bg=PALETTE["bg_card"], width=340, padx=15, pady=15, highlightbackground=PALETTE["border"], highlightthickness=1)
        right_card.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_card.pack_propagate(False)

        tk.Label(right_card, text="Tool Registry & Cognitive State", font=FONTS["subtitle"], bg=PALETTE["bg_card"], fg=PALETTE["text_primary"]).pack(anchor="w", pady=(0, 8))

        tools_info = [
            ("analyze_attendance_defaulters", "Filters attendance records < 75% threshold"),
            ("evaluate_financial_health", "Reconciles fee invoices, revenue, and arrears"),
            ("inspect_student_360", "Multi-table diagnostic profile aggregator"),
            ("audit_timetable_conflicts", "Scans scheduling intervals for double-bookings"),
            ("generate_academic_briefing", "Cross-departmental performance synthesis")
        ]

        for t_name, t_desc in tools_info:
            t_box = tk.Frame(right_card, bg="#F8FAFC", padx=8, pady=6, highlightbackground=PALETTE["border"], highlightthickness=1)
            t_box.pack(fill=tk.X, pady=3)
            tk.Label(t_box, text=f"🔧 {t_name}", font=FONTS["body_bold"], fg=PALETTE["primary"], bg="#F8FAFC").pack(anchor="w")
            tk.Label(t_box, text=t_desc, font=FONTS["small"], fg=PALETTE["text_secondary"], bg="#F8FAFC", wraplength=290, justify="left").pack(anchor="w")

        # Natural Language Query Input Bar at Bottom
        query_bar = tk.Frame(self, bg=PALETTE["bg_card"], padx=15, pady=10, highlightbackground=PALETTE["border"], highlightthickness=1)
        query_bar.pack(fill=tk.X, padx=20, pady=(0, 15))

        tk.Label(query_bar, text="Query Agent:", font=FONTS["body_bold"], bg=PALETTE["bg_card"]).pack(side=tk.LEFT, padx=(0, 6))
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(query_bar, textvariable=self.query_var, font=FONTS["body"])
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.query_entry.bind("<Return>", lambda e: self.dispatch_agent(self.query_var.get()))

        ttk.Button(query_bar, text="Run Agent 🚀", style="Primary.TButton", command=lambda: self.dispatch_agent(self.query_var.get())).pack(side=tk.RIGHT)

        # Welcome message in terminal
        self._print_terminal("=" * 64 + "\n", "divider")
        self._print_terminal("🤖 CAMPUS INTELLIGENCE AGENT INITIALIZED\n", "prompt")
        self._print_terminal("Architecture: ReAct (Reasoning, Action, Observation, Reflection)\n", "thought")
        self._print_terminal("Ready to execute multi-tool analytical queries across live college records.\n", "result")
        self._print_terminal("=" * 64 + "\n\n", "divider")

    def _print_terminal(self, text: str, tag: str = ""):
        self.terminal.insert(tk.END, text, (tag,) if tag else ())
        self.terminal.see(tk.END)

    def dispatch_agent(self, query: str):
        q = query.strip()
        if not q:
            return

        self.query_var.set("")
        self._print_terminal(f"\n[USER QUERY] > {q}\n", "prompt")
        self._print_terminal("-" * 64 + "\n", "divider")

        # Execute agent
        try:
            resp = self.agent.run_agent_task(q)

            # Print Thoughts (Perception & Plan)
            for thought in resp.get("thought_log", []):
                self._print_terminal(f"  🧠 [THOUGHT] {thought}\n", "thought")

            # Print Executed Tools
            for tool in resp.get("executed_tools", []):
                self._print_terminal(f"  ⚡ [ACTION] Dispatched Tool: {tool}()\n", "tool")

            # Print Synthesis
            self._print_terminal(f"\n  🎯 [SYNTHESIS & RECOMMENDATION]:\n", "result")
            self._print_terminal(f"  {resp.get('synthesis', '')}\n\n", "result")
            self._print_terminal("=" * 64 + "\n", "divider")

        except Exception as e:
            self._print_terminal(f"  ❌ [AGENT ERROR] Execution failed: {str(e)}\n", "error")
