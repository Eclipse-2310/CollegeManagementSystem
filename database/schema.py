"""
Database schema definitions and DDL scripts for College Management System.
Normalized toward 3NF with explicit PK, FK, CHECK, UNIQUE, and NOT NULL constraints.
"""

# Dictionary of all table schemas in execution order (respecting foreign key dependencies)
TABLE_SCHEMAS = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('Admin', 'Faculty', 'Student')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """,

    "departments": """
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE,
            department_code TEXT NOT NULL UNIQUE
        );
    """,

    "courses": """
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL UNIQUE,
            department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE CASCADE,
            duration INTEGER NOT NULL CHECK (duration > 0)
        );
    """,

    "faculty": """
        CREATE TABLE IF NOT EXISTS faculty (
            faculty_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
            designation TEXT NOT NULL
        );
    """,

    "students": """
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
            date_of_birth DATE NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            department_id INTEGER NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
            course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE RESTRICT,
            semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
            admission_year INTEGER NOT NULL CHECK (admission_year >= 2000)
        );
    """,

    "subjects": """
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT NOT NULL UNIQUE,
            subject_name TEXT NOT NULL,
            credits INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 10),
            semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
            course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
            faculty_id INTEGER REFERENCES faculty(faculty_id) ON DELETE SET NULL
        );
    """,

    "attendance": """
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
            date DATE NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('Present', 'Absent')),
            UNIQUE (student_id, subject_id, date)
        );
    """,

    "exams": """
        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_name TEXT NOT NULL,
            subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
            exam_date DATE NOT NULL,
            total_marks REAL NOT NULL CHECK (total_marks > 0)
        );
    """,

    "marks": """
        CREATE TABLE IF NOT EXISTS marks (
            mark_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            exam_id INTEGER NOT NULL REFERENCES exams(exam_id) ON DELETE CASCADE,
            marks_obtained REAL NOT NULL CHECK (marks_obtained >= 0),
            UNIQUE (student_id, exam_id)
        );
    """,

    "timetable": """
        CREATE TABLE IF NOT EXISTS timetable (
            timetable_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
            faculty_id INTEGER NOT NULL REFERENCES faculty(faculty_id) ON DELETE CASCADE,
            day TEXT NOT NULL CHECK (day IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')),
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            classroom TEXT NOT NULL,
            CHECK (start_time < end_time)
        );
    """,

    "fees": """
        CREATE TABLE IF NOT EXISTS fees (
            fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            total_fee REAL NOT NULL CHECK (total_fee >= 0),
            paid_amount REAL NOT NULL DEFAULT 0.0 CHECK (paid_amount >= 0),
            pending_amount REAL NOT NULL CHECK (pending_amount >= 0),
            payment_date DATE,
            status TEXT NOT NULL CHECK (status IN ('Paid', 'Partial', 'Pending')),
            CHECK (paid_amount <= total_fee),
            CHECK (pending_amount = total_fee - paid_amount)
        );
    """,

    "library_books": """
        CREATE TABLE IF NOT EXISTS library_books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT NOT NULL UNIQUE,
            quantity INTEGER NOT NULL CHECK (quantity >= 0)
        );
    """,

    "library_transactions": """
        CREATE TABLE IF NOT EXISTS library_transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES library_books(book_id) ON DELETE CASCADE,
            student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
            issue_date DATE NOT NULL,
            return_date DATE,
            status TEXT NOT NULL CHECK (status IN ('Issued', 'Returned', 'Overdue'))
        );
    """,

    "notices": """
        CREATE TABLE IF NOT EXISTS notices (
            notice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            posted_by TEXT NOT NULL,
            posted_date DATE NOT NULL
        );
    """
}

# Helpful performance indexes for foreign keys and common search filters
INDEX_SCHEMAS = [
    "CREATE INDEX IF NOT EXISTS idx_students_roll_no ON students(roll_no);",
    "CREATE INDEX IF NOT EXISTS idx_students_dept ON students(department_id);",
    "CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_attendance_subject_date ON attendance(subject_id, date);",
    "CREATE INDEX IF NOT EXISTS idx_marks_student ON marks(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_marks_exam ON marks(exam_id);",
    "CREATE INDEX IF NOT EXISTS idx_timetable_day ON timetable(day);",
    "CREATE INDEX IF NOT EXISTS idx_fees_student ON fees(student_id);",
    "CREATE INDEX IF NOT EXISTS idx_lib_trans_student ON library_transactions(student_id);"
]
