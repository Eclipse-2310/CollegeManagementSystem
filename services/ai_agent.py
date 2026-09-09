"""
Agentic AI Campus Intelligence Agent for College Management System.
Demonstrates autonomous multi-tool reasoning, planning, tool dispatching,
and executive synthesis for institutional decision support.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import datetime

from database.database import DEFAULT_DB_PATH, fetch_all
from services.student_service import StudentService
from services.attendance_service import AttendanceService
from services.marks_service import MarksService
from services.fee_service import FeeService
from services.admin_service import AdminService
from services.library_service import LibraryService


class AgentTool:
    """Represents a callable tool exposed to the Agentic AI system."""

    def __init__(self, name: str, description: str, func: Callable[..., Any]):
        self.name = name
        self.description = description
        self.func = func

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)

    def __repr__(self) -> str:
        return f"<AgentTool name='{self.name}'>"


class CampusIntelligenceAgent:
    """
    Autonomous Agentic AI for campus administration and student advisory.
    Implements a Perception-Planning-Execution-Reflection (ReAct) cycle:
    1. PERCEIVE: Analyze user request / institutional goal.
    2. PLAN: Determine necessary tools and sequence of operations.
    3. ACT: Dispatch parameterized tools against database services.
    4. OBSERVE: Gather raw metrics and records.
    5. REFLECT & SYNTHESIZE: Formulate strategic diagnosis and actionable recommendations.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.student_svc = StudentService(db_path=self.db_path)
        self.attendance_svc = AttendanceService(db_path=self.db_path)
        self.marks_svc = MarksService(db_path=self.db_path)
        self.fee_svc = FeeService(db_path=self.db_path)
        self.admin_svc = AdminService(db_path=self.db_path)
        self.library_svc = LibraryService(db_path=self.db_path)

        # Tool Registry
        self.tools: Dict[str, AgentTool] = {
            "analyze_attendance_defaulters": AgentTool(
                "analyze_attendance_defaulters",
                "Identifies students whose attendance has fallen below the canonical warning threshold (75%).",
                self._tool_attendance_defaulters
            ),
            "evaluate_financial_health": AgentTool(
                "evaluate_financial_health",
                "Audits fee collection, total revenue, collected funds, and students with outstanding balances.",
                self._tool_financial_health
            ),
            "audit_timetable_conflicts": AgentTool(
                "audit_timetable_conflicts",
                "Scans the weekly master schedule for classroom or faculty double-booking overlaps.",
                self._tool_timetable_conflicts
            ),
            "inspect_student_360": AgentTool(
                "inspect_student_360",
                "Retrieves comprehensive 360-degree profile for a student: enrollment, attendance, grades, fees, library.",
                self._tool_student_360
            ),
            "generate_academic_briefing": AgentTool(
                "generate_academic_briefing",
                "Produces an institutional executive briefing synthesizing KPIs across all college departments.",
                self._tool_executive_briefing
            )
        }

    # ==========================================
    # Tool Implementations
    # ==========================================

    def _tool_attendance_defaulters(self, threshold: float = 75.0) -> Dict[str, Any]:
        defaulters = self.attendance_svc.get_defaulters_list()
        return {
            "threshold_checked": threshold,
            "total_defaulters_flagged": len(defaulters),
            "defaulters": defaulters
        }

    def _tool_financial_health(self) -> Dict[str, Any]:
        summary = self.fee_svc.get_financial_kpi_summary()
        defaulters = self.fee_svc.get_fee_defaulters()
        return {
            "financial_summary": summary,
            "defaulter_count": len(defaulters),
            "top_defaulters": defaulters[:5]
        }

    def _tool_timetable_conflicts(self) -> Dict[str, Any]:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        conflicts = []
        for day in days:
            query = """
                SELECT t.*, s.subject_name, f.name AS faculty_name
                FROM timetable t
                JOIN subjects s ON t.subject_id = s.subject_id
                JOIN faculty f ON t.faculty_id = f.faculty_id
                WHERE t.day = ?
                ORDER BY t.start_time ASC;
            """
            slots = fetch_all(query, (day,), db_path=self.db_path)
            for i in range(len(slots)):
                for j in range(i + 1, len(slots)):
                    s1 = slots[i]
                    s2 = slots[j]
                    if max(s1["start_time"], s2["start_time"]) < min(s1["end_time"], s2["end_time"]):
                        if s1["faculty_id"] == s2["faculty_id"]:
                            conflicts.append(
                                f"{day}: Faculty {s1['faculty_name']} double-booked for "
                                f"'{s1['subject_name']}' and '{s2['subject_name']}' ({s1['start_time']}-{s1['end_time']})."
                            )
                        if s1["classroom"].strip().upper() == s2["classroom"].strip().upper():
                            conflicts.append(
                                f"{day}: Room {s1['classroom']} double-booked between "
                                f"'{s1['subject_name']}' and '{s2['subject_name']}' ({s1['start_time']}-{s1['end_time']})."
                            )
        status = "Verified Clean (Zero Conflicts)" if not conflicts else "Conflicts Detected"
        return {
            "status": status,
            "conflict_count": len(conflicts),
            "detected_conflicts": conflicts
        }


    def _tool_student_360(self, roll_no: str) -> Dict[str, Any]:
        student = self.student_svc.get_by_roll_no(roll_no)
        if not student:
            return {"error": f"Student with roll number '{roll_no}' not found."}
        s_id = student["student_id"]
        att = self.attendance_svc.get_student_overall_attendance(s_id)
        grades = self.marks_svc.get_student_report_card(s_id)
        fees = self.fee_svc.get_student_fee_details(s_id)
        books = self.library_svc.get_active_transactions(student_id=s_id)
        return {
            "student_profile": student,
            "attendance": att,
            "academics": grades,
            "financials": fees,
            "library_circulation": books
        }

    def _tool_executive_briefing(self) -> Dict[str, Any]:
        students = self.student_svc.get_all_students()
        fee_summary = self.fee_svc.get_financial_kpi_summary()
        defaulters = self.attendance_svc.get_defaulters_list()
        books = self.library_svc.get_all_books()
        return {
            "total_students": len(students),
            "fee_collection_rate": (
                round((fee_summary["total_paid_amount"] / fee_summary["total_fee_amount"]) * 100, 1)
                if fee_summary["total_fee_amount"] > 0 else 100.0
            ),
            "attendance_defaulters_count": len(defaulters),
            "library_titles_cataloged": len(books)
        }

    # ==========================================
    # Autonomous Agent Reasoning Engine
    # ==========================================

    def run_agent_task(self, query: str) -> Dict[str, Any]:
        """
        Executes an autonomous ReAct loop:
        1. Parse intent
        2. Formulate step plan
        3. Dispatch tools
        4. Synthesize final response
        """
        query_lower = query.lower()
        thought_log = []
        executed_tools = []

        thought_log.append(f"Received query: '{query}'")

        # Intent Recognition & Planning
        if "attendance" in query_lower or "defaulter" in query_lower or "shortage" in query_lower:
            thought_log.append("Goal Identified: Attendance Risk Evaluation.")
            thought_log.append("Plan: Dispatch 'analyze_attendance_defaulters' with 75% threshold.")
            executed_tools.append("analyze_attendance_defaulters")
            tool_output = self.tools["analyze_attendance_defaulters"].execute(threshold=75.0)

            # Reflection & Advice Synthesis
            count = tool_output["total_defaulters_flagged"]
            summary = (
                f"Agentic Analysis Complete: Identified {count} student(s) below the 75% mandatory attendance threshold. "
                f"Recommended Action: Issue automated warning notices and schedule academic counseling before final examinations."
            )
            return {
                "thought_log": thought_log,
                "executed_tools": executed_tools,
                "tool_data": tool_output,
                "synthesis": summary
            }

        elif "fee" in query_lower or "revenue" in query_lower or "due" in query_lower or "financial" in query_lower:
            thought_log.append("Goal Identified: Institutional Financial Health Audit.")
            thought_log.append("Plan: Dispatch 'evaluate_financial_health' to audit payments and outstanding balances.")
            executed_tools.append("evaluate_financial_health")
            tool_output = self.tools["evaluate_financial_health"].execute()

            summary_data = tool_output["financial_summary"]
            pending = summary_data["total_pending_amount"]
            summary = (
                f"Financial Health Audit Complete: Total Collected: ₹{summary_data['total_paid_amount']:,.2f} | "
                f"Outstanding Dues: ₹{pending:,.2f} across {tool_output['defaulter_count']} student(s). "
                f"Recommended Action: Send automated payment reminders for installment closure."
            )
            return {
                "thought_log": thought_log,
                "executed_tools": executed_tools,
                "tool_data": tool_output,
                "synthesis": summary
            }

        elif "student" in query_lower or "roll" in query_lower or "profile" in query_lower:
            thought_log.append("Goal Identified: 360-degree Student Intelligence Lookup.")
            # Extract roll number if present
            words = query.split()
            target_roll = "CE101"
            for w in words:
                if len(w) >= 3 and any(c.isdigit() for c in w):
                    target_roll = w.strip(",.!?").upper()
                    break

            thought_log.append(f"Plan: Dispatch 'inspect_student_360' for target student {target_roll}.")
            executed_tools.append("inspect_student_360")
            tool_output = self.tools["inspect_student_360"].execute(roll_no=target_roll)

            if "error" in tool_output:
                summary = f"Student Lookup Advisory: {tool_output['error']}"
            else:
                s_name = tool_output["student_profile"]["name"]
                att_pct = tool_output["attendance"]["percentage"]
                sgpa = tool_output["academics"]["sgpa"]
                summary = (
                    f"Student 360 Diagnosis for {s_name} ({target_roll}): Attendance: {att_pct}% | "
                    f"Academic Standing: SGPA {sgpa} ({tool_output['academics']['result_status']}). "
                    f"Profile evaluated across academic, attendance, fee, and library dimensions."
                )
        elif "timetable" in query_lower or "clash" in query_lower or "schedule" in query_lower or "conflict" in query_lower:
            thought_log.append("Goal Identified: Timetable & Master Schedule Conflict Audit.")
            thought_log.append("Plan: Dispatch 'audit_timetable_conflicts' to scan weekly timetable slots for overlapping times.")
            executed_tools.append("audit_timetable_conflicts")
            tool_output = self.tools["audit_timetable_conflicts"].execute()

            if tool_output["conflict_count"] == 0:
                summary = (
                    "Timetable Audit Complete: Master schedule verified clean. "
                    "Zero faculty double-bookings or classroom collisions detected across all weekly intervals."
                )
            else:
                summary = (
                    f"Timetable Audit Alert: Detected {tool_output['conflict_count']} scheduling conflict(s). "
                    f"Action Required: Reassign conflicting slots: {'; '.join(tool_output['detected_conflicts'])}."
                )
            return {
                "thought_log": thought_log,
                "executed_tools": executed_tools,
                "tool_data": tool_output,
                "synthesis": summary
            }

        else:
            thought_log.append("Goal Identified: Comprehensive Campus Executive Briefing.")
            thought_log.append("Plan: Dispatch 'generate_academic_briefing' to synthesize multi-department health.")
            executed_tools.append("generate_academic_briefing")
            tool_output = self.tools["generate_academic_briefing"].execute()
            summary = (
                f"Executive Briefing: Campus is actively serving {tool_output['total_students']} enrolled students with "
                f"a fee realization rate of {tool_output['fee_collection_rate']}%. "
                f"Attendance monitoring has flagged {tool_output['attendance_defaulters_count']} student(s) requiring academic advising."
            )
            return {
                "thought_log": thought_log,
                "executed_tools": executed_tools,
                "tool_data": tool_output,
                "synthesis": summary
            }
