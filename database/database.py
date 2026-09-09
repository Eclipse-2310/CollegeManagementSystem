"""
Database connection management, schema initialization, seeding, and parameterized queries.
Uses standard library sqlite3 with strict foreign key constraints and transaction safety.
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from database.schema import TABLE_SCHEMAS, INDEX_SCHEMAS

# Default path to the SQLite database in the application root directory
DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "college_management.db"
)


class DatabaseConnection:
    """Context manager for SQLite database connections with foreign keys enabled."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # STRICT foreign key constraint enforcement in SQLite
        self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a raw SQLite connection with FK pragma and Row factory enabled."""
    conn = sqlite3.connect(db_path or DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def execute_query(query: str, params: Tuple = (), db_path: Optional[str] = None) -> int:
    """
    Execute a parameterized DML/DDL query (INSERT, UPDATE, DELETE).
    Returns the lastrowid or rowcount.
    """
    with DatabaseConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid or cursor.rowcount


def fetch_one(query: str, params: Tuple = (), db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Fetch a single record as a dictionary."""
    with DatabaseConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: Tuple = (), db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch all matching records as a list of dictionaries."""
    with DatabaseConnection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def initialize_database(db_path: Optional[str] = None) -> None:
    """Create all 14 tables and performance indexes in the database."""
    target_path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    with DatabaseConnection(target_path) as conn:
        cursor = conn.cursor()
        for table_name, ddl in TABLE_SCHEMAS.items():
            cursor.execute(ddl)
        for index_ddl in INDEX_SCHEMAS:
            cursor.execute(index_ddl)


def is_database_seeded(db_path: Optional[str] = None) -> bool:
    """Check if the database contains existing student and user data."""
    try:
        with DatabaseConnection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS count FROM users;")
            user_count = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) AS count FROM students;")
            student_count = cursor.fetchone()["count"]
            return user_count > 0 and student_count >= 20
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return False


# ==========================================
# Parameterized Report Queries (DBMS Module)
# ==========================================

def get_students_with_details(department_id: Optional[int] = None,
                               course_id: Optional[int] = None,
                               search_text: Optional[str] = None,
                               db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Demonstrates SQL JOIN (students + departments + courses) with dynamic WHERE filters.
    """
    query = """
        SELECT 
            s.student_id,
            s.roll_no,
            s.name,
            s.gender,
            s.date_of_birth,
            s.email,
            s.phone,
            s.address,
            s.semester,
            s.admission_year,
            d.department_id,
            d.department_name,
            d.department_code,
            c.course_id,
            c.course_name,
            c.course_code
        FROM students s
        INNER JOIN departments d ON s.department_id = d.department_id
        INNER JOIN courses c ON s.course_id = c.course_id
        WHERE 1=1
    """
    params: List[Any] = []
    if department_id:
        query += " AND s.department_id = ?"
        params.append(department_id)
    if course_id:
        query += " AND s.course_id = ?"
        params.append(course_id)
    if search_text:
        query += " AND (s.name LIKE ? OR s.roll_no LIKE ? OR s.email LIKE ?)"
        like_term = f"%{search_text}%"
        params.extend([like_term, like_term, like_term])
    query += " ORDER BY s.roll_no ASC"
    return fetch_all(query, tuple(params), db_path=db_path)


def get_attendance_percentage_report(subject_id: Optional[int] = None,
                                      student_id: Optional[int] = None,
                                      db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Demonstrates SQL GROUP BY, COUNT, SUM with conditional CASE aggregation.
    Formula: (Present / Total) * 100
    """
    query = """
        SELECT 
            s.student_id,
            s.roll_no,
            s.name AS student_name,
            sub.subject_id,
            sub.subject_name,
            sub.subject_code,
            COUNT(a.attendance_id) AS total_classes,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS attended_classes,
            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS missed_classes,
            ROUND(
                (CAST(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS REAL) / 
                 CASE WHEN COUNT(a.attendance_id) = 0 THEN 1 ELSE COUNT(a.attendance_id) END) * 100, 
                2
            ) AS attendance_percentage
        FROM students s
        CROSS JOIN subjects sub
        LEFT JOIN attendance a ON s.student_id = a.student_id AND sub.subject_id = a.subject_id
        WHERE 1=1
    """
    params: List[Any] = []
    if subject_id:
        query += " AND sub.subject_id = ?"
        params.append(subject_id)
    if student_id:
        query += " AND s.student_id = ?"
        params.append(student_id)
    query += """
        GROUP BY s.student_id, sub.subject_id
        HAVING total_classes > 0
        ORDER BY s.roll_no ASC, sub.subject_name ASC
    """
    return fetch_all(query, tuple(params), db_path=db_path)


def get_student_results_report(student_id: Optional[int] = None,
                               exam_id: Optional[int] = None,
                               db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Demonstrates multi-table JOINs (marks + exams + subjects + students)
    with SQL calculations for marks percentage and letter grade mapping.
    """
    query = """
        SELECT 
            m.mark_id,
            s.student_id,
            s.roll_no,
            s.name AS student_name,
            e.exam_id,
            e.exam_name,
            e.exam_date,
            sub.subject_name,
            sub.subject_code,
            m.marks_obtained,
            e.total_marks,
            ROUND((m.marks_obtained / e.total_marks) * 100, 2) AS percentage,
            CASE 
                WHEN (m.marks_obtained / e.total_marks) * 100 >= 90.0 THEN 'A+'
                WHEN (m.marks_obtained / e.total_marks) * 100 >= 80.0 THEN 'A'
                WHEN (m.marks_obtained / e.total_marks) * 100 >= 70.0 THEN 'B+'
                WHEN (m.marks_obtained / e.total_marks) * 100 >= 60.0 THEN 'B'
                WHEN (m.marks_obtained / e.total_marks) * 100 >= 50.0 THEN 'C'
                WHEN (m.marks_obtained / e.total_marks) * 100 >= 40.0 THEN 'D'
                ELSE 'F'
            END AS grade
        FROM marks m
        INNER JOIN students s ON m.student_id = s.student_id
        INNER JOIN exams e ON m.exam_id = e.exam_id
        INNER JOIN subjects sub ON e.subject_id = sub.subject_id
        WHERE 1=1
    """
    params: List[Any] = []
    if student_id:
        query += " AND s.student_id = ?"
        params.append(student_id)
    if exam_id:
        query += " AND e.exam_id = ?"
        params.append(exam_id)
    query += " ORDER BY s.roll_no ASC, e.exam_date DESC"
    return fetch_all(query, tuple(params), db_path=db_path)


def get_department_statistics(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Demonstrates SQL aggregation (COUNT, AVG) grouped by department.
    """
    query = """
        SELECT 
            d.department_id,
            d.department_name,
            d.department_code,
            COUNT(DISTINCT s.student_id) AS student_count,
            COUNT(DISTINCT f.faculty_id) AS faculty_count,
            COUNT(DISTINCT c.course_id) AS course_count,
            COALESCE(ROUND(AVG(m.marks_obtained / e.total_marks * 100), 2), 0.0) AS avg_marks_percentage
        FROM departments d
        LEFT JOIN students s ON d.department_id = s.department_id
        LEFT JOIN faculty f ON d.department_id = f.department_id
        LEFT JOIN courses c ON d.department_id = c.department_id
        LEFT JOIN marks m ON s.student_id = m.student_id
        LEFT JOIN exams e ON m.exam_id = e.exam_id
        GROUP BY d.department_id
        ORDER BY d.department_name ASC
    """
    return fetch_all(query, (), db_path=db_path)


def get_fee_collection_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Demonstrates SQL aggregate SUM and COUNT across financial records.
    """
    query = """
        SELECT 
            COUNT(fee_id) AS total_invoices,
            COALESCE(SUM(total_fee), 0.0) AS total_fee_amount,
            COALESCE(SUM(paid_amount), 0.0) AS total_paid_amount,
            COALESCE(SUM(pending_amount), 0.0) AS total_pending_amount,
            SUM(CASE WHEN status = 'Paid' THEN 1 ELSE 0 END) AS paid_count,
            SUM(CASE WHEN status = 'Partial' THEN 1 ELSE 0 END) AS partial_count,
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) AS pending_count
        FROM fees
    """
    result = fetch_one(query, (), db_path=db_path)
    return result if result else {
        "total_invoices": 0,
        "total_fee_amount": 0.0,
        "total_paid_amount": 0.0,
        "total_pending_amount": 0.0,
        "paid_count": 0,
        "partial_count": 0,
        "pending_count": 0
    }


def get_library_circulation_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Demonstrates library catalog and circulation status counts.
    """
    query = """
        SELECT 
            (SELECT COUNT(*) FROM library_books) AS unique_titles,
            (SELECT COALESCE(SUM(quantity), 0) FROM library_books) AS available_copies,
            (SELECT COUNT(*) FROM library_transactions WHERE status = 'Issued') AS currently_issued,
            (SELECT COUNT(*) FROM library_transactions WHERE status = 'Returned') AS returned_count,
            (SELECT COUNT(*) FROM library_transactions WHERE status = 'Overdue') AS overdue_count
    """
    result = fetch_one(query, (), db_path=db_path)
    return result if result else {
        "unique_titles": 0,
        "available_copies": 0,
        "currently_issued": 0,
        "returned_count": 0,
        "overdue_count": 0
    }


def seed_initial_data(db_path: Optional[str] = None) -> None:
    """
    Seeds comprehensive, realistic academic data on first run:
    - 3 Departments
    - 3 Courses
    - 6 Faculty Members
    - 25 Students (Semesters 1-8)
    - 10 Subjects with credits
    - Attendance records
    - 3 Examinations & Marks
    - 25 Fee Ledgers (Paid/Partial/Pending)
    - 15 Library Books & Transactions
    - 5 Campus Notices
    - Default Demo Logins (admin, faculty1, student1) with salted SHA-256 hashes
    """
    from utils.security import hash_password

    # 1. Users
    demo_users = [
        ("admin", hash_password("admin123"), "Admin"),
        ("faculty1", hash_password("faculty123"), "Faculty"),
        ("student1", hash_password("student123"), "Student")
    ]
    for u, h, r in demo_users:
        execute_query(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?);",
            (u, h, r), db_path=db_path
        )

    # 2. Departments
    depts = [
        ("Computer Engineering", "CE"),
        ("Information Technology", "IT"),
        ("Electronics & Telecommunication", "EXTC")
    ]
    dept_ids = {}
    for name, code in depts:
        d_id = execute_query(
            "INSERT OR IGNORE INTO departments (department_name, department_code) VALUES (?, ?);",
            (name, code), db_path=db_path
        )
        row = fetch_one("SELECT department_id FROM departments WHERE department_code = ?", (code,), db_path=db_path)
        dept_ids[code] = row["department_id"] if row else d_id

    # 3. Courses
    courses_data = [
        ("B.E. Computer Engineering", "BE-CE", dept_ids["CE"], 4),
        ("B.E. Information Technology", "BE-IT", dept_ids["IT"], 4),
        ("B.E. Electronics & Telecom", "BE-EXTC", dept_ids["EXTC"], 4)
    ]
    course_ids = {}
    for c_name, c_code, d_id, dur in courses_data:
        c_id = execute_query(
            "INSERT OR IGNORE INTO courses (course_name, course_code, department_id, duration) VALUES (?, ?, ?, ?);",
            (c_name, c_code, d_id, dur), db_path=db_path
        )
        row = fetch_one("SELECT course_id FROM courses WHERE course_code = ?", (c_code,), db_path=db_path)
        course_ids[c_code] = row["course_id"] if row else c_id

    # 4. Faculty
    faculty_data = [
        ("Dr. Alan Turing", "faculty1@college.edu", "9876543201", dept_ids["CE"], "Professor & HOD"),
        ("Prof. Ada Lovelace", "ada.fac@college.edu", "9876543202", dept_ids["CE"], "Associate Professor"),
        ("Dr. Claude Shannon", "shannon@college.edu", "9876543203", dept_ids["IT"], "Professor & HOD"),
        ("Prof. Grace Hopper", "grace.fac@college.edu", "9876543204", dept_ids["IT"], "Assistant Professor"),
        ("Dr. Heinrich Hertz", "hertz@college.edu", "9876543205", dept_ids["EXTC"], "Professor & HOD"),
        ("Prof. Nikola Tesla", "tesla@college.edu", "9876543206", dept_ids["EXTC"], "Associate Professor")
    ]
    faculty_ids = []
    for f_name, f_email, f_phone, f_dept, f_desig in faculty_data:
        f_id = execute_query(
            "INSERT OR IGNORE INTO faculty (name, email, phone, department_id, designation) VALUES (?, ?, ?, ?, ?);",
            (f_name, f_email, f_phone, f_dept, f_desig), db_path=db_path
        )
        row = fetch_one("SELECT faculty_id FROM faculty WHERE email = ?", (f_email,), db_path=db_path)
        faculty_ids.append(row["faculty_id"] if row else f_id)

    # 5. Subjects
    subjects_data = [
        ("CE301", "Data Structures & Algorithms", 4, 3, course_ids["BE-CE"], faculty_ids[0]),
        ("CE401", "Database Management Systems", 4, 4, course_ids["BE-CE"], faculty_ids[1]),
        ("CE501", "Operating Systems", 4, 5, course_ids["BE-CE"], faculty_ids[0]),
        ("CE601", "Computer Networks", 4, 6, course_ids["BE-CE"], faculty_ids[1]),
        ("IT301", "Object Oriented Programming", 4, 3, course_ids["BE-IT"], faculty_ids[2]),
        ("IT401", "Web Application Development", 4, 4, course_ids["BE-IT"], faculty_ids[3]),
        ("IT501", "Cloud Computing & DevOps", 4, 5, course_ids["BE-IT"], faculty_ids[2]),
        ("IT601", "Artificial Intelligence & Agents", 4, 6, course_ids["BE-IT"], faculty_ids[3]),
        ("EX301", "Digital Electronics & Logic Design", 4, 3, course_ids["BE-EXTC"], faculty_ids[4]),
        ("EX401", "Signals & Linear Systems", 4, 4, course_ids["BE-EXTC"], faculty_ids[5])
    ]
    subject_ids = {}
    for code, s_name, credits, sem, c_id, f_id in subjects_data:
        s_id = execute_query(
            "INSERT OR IGNORE INTO subjects (subject_code, subject_name, credits, semester, course_id, faculty_id) VALUES (?, ?, ?, ?, ?, ?);",
            (code, s_name, credits, sem, c_id, f_id), db_path=db_path
        )
        row = fetch_one("SELECT subject_id FROM subjects WHERE subject_code = ?", (code,), db_path=db_path)
        subject_ids[code] = row["subject_id"] if row else s_id

    # 6. Students (25 students across departments and semesters)
    students_raw = [
        # CE Students
        ("CE101", "Aarav Sharma", "Male", "2004-03-12", "student1@college.edu", "9820011001", "Bandra, Mumbai", dept_ids["CE"], course_ids["BE-CE"], 4, 2023),
        ("CE102", "Ananya Iyer", "Female", "2004-07-21", "ananya@college.edu", "9820011002", "Dadar, Mumbai", dept_ids["CE"], course_ids["BE-CE"], 4, 2023),
        ("CE103", "Rohan Verma", "Male", "2003-11-05", "rohan@college.edu", "9820011003", "Andheri, Mumbai", dept_ids["CE"], course_ids["BE-CE"], 4, 2023),
        ("CE104", "Pooja Hegde", "Female", "2004-01-18", "pooja@college.edu", "9820011004", "Thane, Mumbai", dept_ids["CE"], course_ids["BE-CE"], 4, 2023),
        ("CE105", "Kabir Khan", "Male", "2003-09-30", "kabir@college.edu", "9820011005", "Kurla, Mumbai", dept_ids["CE"], course_ids["BE-CE"], 4, 2023),
        ("CE106", "Sneha Patil", "Female", "2005-04-14", "sneha@college.edu", "9820011006", "Vashi, Navi Mumbai", dept_ids["CE"], course_ids["BE-CE"], 2, 2024),
        ("CE107", "Varun Nair", "Male", "2005-08-25", "varun@college.edu", "9820011007", "Panvel, Navi Mumbai", dept_ids["CE"], course_ids["BE-CE"], 2, 2024),
        ("CE108", "Diya Kulkarni", "Female", "2002-12-08", "diya@college.edu", "9820011008", "Kothrud, Pune", dept_ids["CE"], course_ids["BE-CE"], 6, 2022),
        ("CE109", "Arjun Deshmukh", "Male", "2002-06-19", "arjun@college.edu", "9820011009", "Shivajinagar, Pune", dept_ids["CE"], course_ids["BE-CE"], 6, 2022),

        # IT Students
        ("IT101", "Ishaan Joshi", "Male", "2004-02-11", "ishaan@college.edu", "9820012001", "Borivali, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 4, 2023),
        ("IT102", "Meera Sen", "Female", "2004-05-23", "meera@college.edu", "9820012002", "Kandivali, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 4, 2023),
        ("IT103", "Siddharth Rao", "Male", "2003-10-14", "siddharth@college.edu", "9820012003", "Goregaon, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 4, 2023),
        ("IT104", "Tanvi Mehta", "Female", "2004-08-03", "tanvi@college.edu", "9820012004", "Malad, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 4, 2023),
        ("IT105", "Aditya Kadam", "Male", "2005-03-29", "aditya@college.edu", "9820012005", "Nerul, Navi Mumbai", dept_ids["IT"], course_ids["BE-IT"], 2, 2024),
        ("IT106", "Rhea Dsouza", "Female", "2005-09-17", "rhea@college.edu", "9820012006", "Bandra, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 2, 2024),
        ("IT107", "Kunal Shinde", "Male", "2002-11-22", "kunal@college.edu", "9820012007", "Chembur, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 6, 2022),
        ("IT108", "Neha Reddy", "Female", "2002-04-05", "neha@college.edu", "9820012008", "Sion, Mumbai", dept_ids["IT"], course_ids["BE-IT"], 6, 2022),

        # EXTC Students
        ("EX101", "Devendra Singh", "Male", "2004-01-20", "devendra@college.edu", "9820013001", "Mulund, Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 4, 2023),
        ("EX102", "Priyanka Roy", "Female", "2004-06-16", "priyanka@college.edu", "9820013002", "Ghatkopar, Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 4, 2023),
        ("EX103", "Yash Chopra", "Male", "2003-12-01", "yash@college.edu", "9820013003", "Powai, Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 4, 2023),
        ("EX104", "Shreya Bhat", "Female", "2004-09-10", "shreya@college.edu", "9820013004", "Vikhroli, Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 4, 2023),
        ("EX105", "Harsh Vardhan", "Male", "2005-02-18", "harsh@college.edu", "9820013005", "Kalyan, Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 2, 2024),
        ("EX106", "Kavya Menon", "Female", "2005-07-07", "kavya@college.edu", "9820013006", "Dombivli, Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 2, 2024),
        ("EX107", "Pranav Joshi", "Male", "2002-05-13", "pranav@college.edu", "9820013007", "Airoli, Navi Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 6, 2022),
        ("EX108", "Sakshi Bansal", "Female", "2002-10-27", "sakshi@college.edu", "9820013008", "Ghansoli, Navi Mumbai", dept_ids["EXTC"], course_ids["BE-EXTC"], 6, 2022)
    ]

    student_id_map = {}
    for roll, name, gen, dob, email, ph, addr, d_id, c_id, sem, adm_yr in students_raw:
        execute_query(
            """INSERT OR IGNORE INTO students 
               (roll_no, name, gender, date_of_birth, email, phone, address, department_id, course_id, semester, admission_year)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (roll, name, gen, dob, email, ph, addr, d_id, c_id, sem, adm_yr),
            db_path=db_path
        )
        row = fetch_one("SELECT student_id FROM students WHERE roll_no = ?", (roll,), db_path=db_path)
        student_id_map[roll] = row["student_id"]

    # 7. Attendance (Multiple dates across subjects)
    attendance_dates = ["2026-08-25", "2026-08-26", "2026-08-27", "2026-08-28", "2026-08-29",
                        "2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05"]
    sub_ce_db = subject_ids["CE401"]
    sub_it_web = subject_ids["IT401"]

    for idx, (roll, s_id) in enumerate(student_id_map.items()):
        # Intentionally create some defaulters (<75%) for viva demo: e.g. student index 4, 8, 12
        is_defaulter_demo = (idx in (4, 8, 12, 19))
        for day_idx, att_date in enumerate(attendance_dates):
            # Target subject based on course
            sub_id = sub_ce_db if "CE" in roll else sub_it_web
            if is_defaulter_demo:
                status = "Present" if day_idx < 4 else "Absent"  # 4/10 = 40%
            else:
                status = "Present" if day_idx != 7 else "Absent" # 9/10 = 90%
            execute_query(
                "INSERT OR IGNORE INTO attendance (student_id, subject_id, date, status) VALUES (?, ?, ?, ?);",
                (s_id, sub_id, att_date, status), db_path=db_path
            )

    # 8. Exams & Marks
    exam_1_id = execute_query(
        "INSERT OR IGNORE INTO exams (exam_name, subject_id, exam_date, total_marks) VALUES (?, ?, ?, ?);",
        ("Midterm Examination", sub_ce_db, "2026-08-30", 100.0), db_path=db_path
    )
    exam_2_id = execute_query(
        "INSERT OR IGNORE INTO exams (exam_name, subject_id, exam_date, total_marks) VALUES (?, ?, ?, ?);",
        ("Midterm Examination", sub_it_web, "2026-08-31", 100.0), db_path=db_path
    )
    exam_3_id = execute_query(
        "INSERT OR IGNORE INTO exams (exam_name, subject_id, exam_date, total_marks) VALUES (?, ?, ?, ?);",
        ("Unit Test 1", sub_ce_db, "2026-09-02", 50.0), db_path=db_path
    )

    for idx, (roll, s_id) in enumerate(student_id_map.items()):
        ex_id = exam_1_id if "CE" in roll else exam_2_id
        # Range of marks from 45 to 98
        score = min(98.0, 50.0 + (idx * 2.1))
        execute_query(
            "INSERT OR IGNORE INTO marks (student_id, exam_id, marks_obtained) VALUES (?, ?, ?);",
            (s_id, ex_id, score), db_path=db_path
        )
        if "CE" in roll:
            execute_query(
                "INSERT OR IGNORE INTO marks (student_id, exam_id, marks_obtained) VALUES (?, ?, ?);",
                (s_id, exam_3_id, score * 0.48), db_path=db_path
            )

    # 9. Fees (Strict pending = total - paid)
    for idx, (roll, s_id) in enumerate(student_id_map.items()):
        total_fee = 75000.0
        if idx % 3 == 0:
            paid = 75000.0
            st = "Paid"
            p_date = "2026-08-10"
        elif idx % 3 == 1:
            paid = 45000.0
            st = "Partial"
            p_date = "2026-08-15"
        else:
            paid = 0.0
            st = "Pending"
            p_date = None
        pending = total_fee - paid
        execute_query(
            """INSERT OR IGNORE INTO fees (student_id, total_fee, paid_amount, pending_amount, payment_date, status)
               VALUES (?, ?, ?, ?, ?, ?);""",
            (s_id, total_fee, paid, pending, p_date, st), db_path=db_path
        )

    # 10. Library Books
    books_data = [
        ("Introduction to Algorithms (CLRS)", "Cormen, Leiserson, Rivest, Stein", "Computer Science", "978-0262033848", 5),
        ("Clean Code: Agile Software Craftsmanship", "Robert C. Martin", "Software Engineering", "978-0132350884", 4),
        ("Operating System Concepts (Dinosaur)", "Silberschatz, Galvin, Gagne", "Computer Science", "978-1118063330", 6),
        ("Database System Concepts", "Silberschatz, Korth, Sudarshan", "DBMS", "978-0078022159", 5),
        ("Computer Networks", "Andrew S. Tanenbaum", "Networks", "978-0132126953", 4),
        ("Artificial Intelligence: Modern Approach", "Stuart Russell, Peter Norvig", "AI", "978-0136042594", 3),
        ("Design Patterns: Reusable Elements", "Gamma, Helm, Johnson, Vlissides", "Software Architecture", "978-0201633610", 4),
        ("Python Crash Course", "Eric Matthes", "Programming", "978-1593279288", 6),
        ("The Pragmatic Programmer", "David Thomas, Andrew Hunt", "Software Engineering", "978-0135957059", 4),
        ("Head First Design Patterns", "Eric Freeman, Elisabeth Robson", "Programming", "978-0596007126", 5),
        ("Compilers: Principles, Techniques, & Tools", "Aho, Lam, Sethi, Ullman", "Computer Science", "978-0321486813", 2),
        ("Modern Operating Systems", "Andrew S. Tanenbaum", "Computer Science", "978-0133591620", 3),
        ("Electronic Principles", "Albert Malvino, David Bates", "Electronics", "978-0073373881", 4),
        ("Signals and Systems", "Alan V. Oppenheim", "Electronics", "978-0138147570", 3),
        ("Digital Design", "M. Morris Mano, Michael D. Ciletti", "Electronics", "978-0132774208", 5)
    ]
    book_ids = []
    for title, author, cat, isbn, qty in books_data:
        b_id = execute_query(
            "INSERT OR IGNORE INTO library_books (title, author, category, isbn, quantity) VALUES (?, ?, ?, ?, ?);",
            (title, author, cat, isbn, qty), db_path=db_path
        )
        row = fetch_one("SELECT book_id FROM library_books WHERE isbn = ?", (isbn,), db_path=db_path)
        book_ids.append(row["book_id"] if row else b_id)

    # 11. Library Transactions
    s_ids = list(student_id_map.values())
    execute_query(
        "INSERT OR IGNORE INTO library_transactions (book_id, student_id, issue_date, return_date, status) VALUES (?, ?, ?, ?, 'Returned');",
        (book_ids[0], s_ids[0], "2026-08-15", "2026-08-25"), db_path=db_path
    )
    execute_query(
        "INSERT OR IGNORE INTO library_transactions (book_id, student_id, issue_date, status) VALUES (?, ?, ?, 'Issued');",
        (book_ids[1], s_ids[0], "2026-09-01"), db_path=db_path
    )
    execute_query(
        "INSERT OR IGNORE INTO library_transactions (book_id, student_id, issue_date, status) VALUES (?, ?, ?, 'Issued');",
        (book_ids[2], s_ids[1], "2026-09-02"), db_path=db_path
    )
    execute_query(
        "INSERT OR IGNORE INTO library_transactions (book_id, student_id, issue_date, status) VALUES (?, ?, ?, 'Issued');",
        (book_ids[3], s_ids[2], "2026-09-03"), db_path=db_path
    )

    # 12. Campus Notices
    notices_data = [
        ("Term Fee Payment Deadline", "All students are notified that the final installment of the term fee must be paid before September 20, 2026 to avoid late penalties.", "Accounts Section", "2026-09-01"),
        ("Midterm Examination Schedule Released", "The timetable for Semester 4 Midterm Examinations has been published. Check your department notice board for classroom allocations.", "Exam Cell", "2026-09-03"),
        ("Annual Technical Symposium 'Technovate 2026'", "Registrations are now open for coding, robotics, and project presentation competitions. Cash prizes worth ₹1,00,000 to be won!", "Student Council", "2026-09-05"),
        ("Guest Lecture on Agentic AI & Modern Software Engineering", "A distinguished seminar on Agentic AI Architectures by Google DeepMind experts is scheduled for Friday at 2:00 PM in the Main Auditorium.", "Dean Academics", "2026-09-07"),
        ("Library Book Return & Clearance Notice", "All students with books overdue for more than 14 days are requested to renew or return their copies to maintain borrowing eligibility.", "Chief Librarian", "2026-09-08")
    ]
    for n_title, n_desc, n_by, n_date in notices_data:
        execute_query(
            "INSERT OR IGNORE INTO notices (title, description, posted_by, posted_date) VALUES (?, ?, ?, ?);",
            (n_title, n_desc, n_by, n_date), db_path=db_path
        )

    # 13. Timetable Slots
    sample_timetable = [
        (subject_ids["CE301"], faculty_ids[0], "Monday", "09:00", "10:00", "LH-101"),
        (subject_ids["CE401"], faculty_ids[1], "Monday", "10:15", "11:15", "LH-101"),
        (subject_ids["CE501"], faculty_ids[0], "Tuesday", "09:00", "10:00", "LH-102"),
        (subject_ids["IT301"], faculty_ids[2], "Wednesday", "11:30", "12:30", "LH-201"),
        (subject_ids["IT401"], faculty_ids[3], "Thursday", "14:00", "15:00", "LH-202"),
        (subject_ids["EX301"], faculty_ids[4], "Friday", "10:00", "11:00", "LH-301")
    ]
    for sub, fac, day, s_time, e_time, room in sample_timetable:
        execute_query(
            """INSERT OR IGNORE INTO timetable (subject_id, faculty_id, day, start_time, end_time, classroom)
               VALUES (?, ?, ?, ?, ?, ?);""",
            (sub, fac, day, s_time, e_time, room), db_path=db_path
        )


def ensure_database_ready(db_path: Optional[str] = None) -> None:
    """
    Checks if database is initialized and seeded; if not, automatically creates
    and seeds it on first run. Idempotent.
    """
    target = db_path or DEFAULT_DB_PATH
    initialize_database(target)
    if not is_database_seeded(target):
        seed_initial_data(target)

