# Task Checklist: College Management System (CMS) Desktop Application

- [x] **Phase 0: Scaffold & Implementation Plan**
  - [x] Create canonical Knowledge Items for DB schema, grading scale, attendance warning, demo logins, and module-to-file mapping
  - [x] Create comprehensive `implementation_plan.md` artifact
  - [x] Scaffold folder structure and all module files with initial stubs and docstrings
  - [x] Verify `main.py` imports cleanly with zero errors

- [x] **Phase 1: Database Layer & Schema (DBMS Concepts)**
  - [x] Implement `database/schema.py` with 14 normalized tables and explicit constraints (PK/FK/CHECK/UNIQUE/NOT NULL)
  - [x] Implement `database/database.py` with thread-safe connections, foreign key pragmas, and parameterized report queries
  - [x] Create `tests/test_phase1_db.py` headless test suite
  - [x] Verify: Execute `test_phase1_db.py` verifying schema, foreign keys, and CRUD across all 14 tables

- [x] **Phase 2: OOP Model Layer**
  - [x] Implement `models/user.py` with `User` ABC and polymorphic `display_dashboard()` for `Admin`, `Faculty`, and `Student`
  - [x] Implement domain models: `Student`, `Faculty`, `Course`, `Department`, `Subject`, `Attendance`, `Exam`, `Marks`, `Fee`, `LibraryBook`, `LibraryTransaction`, `Notice`
  - [x] Create `tests/test_phase2_oop.py` headless test suite
  - [x] Verify: Execute `test_phase2_oop.py` asserting encapsulation, inheritance, and polymorphic output

- [x] **Phase 3: Data Structures (Genuine Integration)**
  - [x] Implement `data_structures/stack.py` with Undo/Action History tracking
  - [x] Implement `data_structures/queue.py` with Administrative/Library Request Queue
  - [x] Implement `data_structures/linked_list.py` with Notice Board node chain
  - [x] Integrate $O(1)$ Hash Dictionaries in service layer with asymptotic complexity documentation
  - [x] Create `tests/test_phase3_ds.py` headless test suite
  - [x] Verify: Execute `test_phase3_ds.py` exercising real service call sites

- [x] **Phase 4: Algorithms (Searching & Sorting)**
  - [x] Implement `algorithms/searching.py` with Linear Search and Binary Search plus step/comparison counting
  - [x] Implement `algorithms/sorting.py` with Bubble Sort, Selection Sort, and Merge Sort supporting multi-attribute keys
  - [x] Create `tests/test_phase4_algo.py` headless test suite
  - [x] Verify: Execute `test_phase4_algo.py` verifying sort equivalence and search comparison counts

- [x] **Phase 5: Services & Business Rules Layer**
  - [x] Implement `services/student_service.py` with CRUD, caching, and undo stack
  - [x] Implement `services/attendance_service.py` with threshold calculation and defaulter list (<75%)
  - [x] Implement `services/marks_service.py` with grade evaluation (A+ to F) and boundary validation
  - [x] Implement `services/library_service.py` with book circulation and request queue
  - [x] Implement `services/fee_service.py` with pending calculation and negative amount rejection
  - [x] Implement `services/admin_service.py` with timetable double-booking conflict detection
  - [x] Implement `services/ai_agent.py` autonomous Agentic AI campus assistant with ReAct cycle
  - [x] Create `tests/test_phase5_services.py` headless test suite
  - [x] Verify: Execute `test_phase5_services.py` with edge cases and boundary tests

- [x] **Phase 6: Validation, Exception Handling & Security**
  - [x] Implement `utils/validation.py` for user input regex and range checks
  - [x] Implement `utils/security.py` for salted SHA-256 hashing, session state, and RBAC
  - [x] Implement universal try/except/finally exception handling wrappers
  - [x] Create `tests/test_phase6_security.py` headless test suite
  - [x] Verify: Execute `test_phase6_security.py` asserting user-friendly error messages and zero crashes

- [x] **Phase 7: File Handling (CSV / JSON)**
  - [x] Implement `utils/export.py` with CSV export/import and full JSON database backup/restore
  - [x] Create `tests/test_phase7_export.py` headless test suite
  - [x] Verify: Execute `test_phase7_export.py` asserting record count and data fidelity match database

- [ ] **Phase 8: Modern GUI & Academic Demo Panels**
  - [ ] Implement `gui/styles.py` with modern visual styling and color palette
  - [ ] Implement `gui/canvas_charts.py` for zero-dependency native Tkinter Canvas charts
  - [ ] Implement `gui/login.py` dialog with role-switcher demo buttons
  - [ ] Implement `gui/dashboard.py` shell with sidebar, metric cards, and charts
  - [ ] Implement feature screens: `students.py`, `faculty.py`, `attendance.py`, `exams.py`, `timetable.py`, `library.py`, `fees.py`, `notices.py`, `reports.py`, `settings.py`
  - [ ] Implement Academic Demo Panels: `gui/dsa_demo.py` and `gui/dbms_demo.py`
  - [ ] Create `tests/test_phase8_gui_logic.py` headless GUI test suite
  - [ ] Verify: Execute `test_phase8_gui_logic.py` asserting data bindings and controllers

- [ ] **Phase 9: Sample Data & First-Run Initialization**
  - [ ] Implement database seeding in `database/database.py` with >=25 students, 6 faculty, 3 depts, 3 courses, 10 subjects, attendance, marks, fees, library, notices, and 3 demo user accounts
  - [ ] Verify first-run auto-seeding upon database absence

- [ ] **Phase 10: Full Regression Pass & Documentation**
  - [ ] Implement and execute `tests/test_regression.py` running all test suites back-to-back
  - [ ] Verify app startup and idempotency across repeated launches
  - [ ] Write comprehensive `README.md`
  - [ ] Write detailed `ACADEMIC_DOCUMENTATION.md` for viva evaluation
  - [ ] Generate final `walkthrough.md` artifact
