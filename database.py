"""
Database module for Student Record Management System.
Handles SQLite connectivity, schema initialization, CRUD operations, and analytics queries.
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'students.db')
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')


@contextmanager
def get_db():
    """Context manager for SQLite connection with automatic closing and WAL mode."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database schema from schema.sql."""
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with get_db() as conn:
        conn.executescript(schema_sql)
        conn.commit()


def seed_sample_data(force=False):
    """Seed initial student records if the database is empty or if forced."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM students")
        row = cursor.fetchone()
        
        if row and row['count'] > 0 and not force:
            return False  # Already seeded

        if force:
            cursor.execute("DELETE FROM students")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
            conn.commit()

        sample_students = [
            (
                "STU-2026-001", "Aria", "Montgomery", "aria.montgomery@university.edu",
                "+1 (555) 234-5678", "Computer Science & AI", "3rd Year", 3.92, "Active",
                "2004-03-14", "Female", "742 Evergreen Terrace, Seattle, WA",
                "Ella Montgomery (Mother) - +1 (555) 876-5432",
                "Specializing in Machine Learning and Computer Vision. Dean's Honor Roll recipient for 4 consecutive semesters."
            ),
            (
                "STU-2026-002", "Ethan", "Chen", "ethan.chen@university.edu",
                "+1 (555) 345-6789", "Data Science & Analytics", "4th Year", 3.85, "Active",
                "2003-08-22", "Male", "1204 Pine St, San Francisco, CA",
                "Michael Chen (Father) - +1 (555) 987-6543",
                "Lead researcher on neural network optimization. President of the University Data Science Club."
            ),
            (
                "STU-2026-003", "Sophia", "Rodriguez", "sophia.rodriguez@university.edu",
                "+1 (555) 456-7890", "Cybersecurity & Networks", "2nd Year", 3.74, "Active",
                "2005-01-19", "Female", "580 Oak Avenue, Austin, TX",
                "Carlos Rodriguez (Father) - +1 (555) 432-1098",
                "Member of Collegiate Cyber Defense Competition team. Active in ethical hacking workshops."
            ),
            (
                "STU-2026-004", "Marcus", "Vance", "marcus.vance@university.edu",
                "+1 (555) 567-8901", "Software Engineering", "3rd Year", 3.61, "Active",
                "2004-11-05", "Male", "882 Maple Blvd, Chicago, IL",
                "Dianne Vance (Mother) - +1 (555) 654-3210",
                "Full-stack web developer enthusiast. Mentoring 1st year students in algorithmic problem solving."
            ),
            (
                "STU-2026-005", "Zara", "Patel", "zara.patel@university.edu",
                "+1 (555) 678-9012", "Biomedical Engineering", "4th Year", 3.98, "Active",
                "2003-06-30", "Female", "315 Cedar Way, Boston, MA",
                "Amit Patel (Father) - +1 (555) 765-4321",
                "Valedictorian candidate. Published co-author in the Journal of Bio-Sensors and Medical Devices."
            ),
            (
                "STU-2026-006", "Lucas", "Dubois", "lucas.dubois@university.edu",
                "+1 (555) 789-0123", "Electrical & Computer Eng", "2nd Year", 3.42, "On Leave",
                "2005-09-12", "Male", "409 Elm Street, Denver, CO",
                "Claire Dubois (Mother) - +1 (555) 321-0987",
                "Participating in an accredited 6-month industrial robotics engineering co-op program."
            ),
            (
                "STU-2026-007", "Elena", "Rostova", "elena.rostova@university.edu",
                "+1 (555) 890-1234", "Computer Science & AI", "4th Year", 3.88, "Graduated",
                "2002-12-04", "Female", "901 Birch Lane, New York, NY",
                "Igor Rostov (Father) - +1 (555) 210-9876",
                "Graduated Magna Cum Laude. Accepted associate software engineer role at top tech firm."
            ),
            (
                "STU-2026-008", "David", "Kim", "david.kim@university.edu",
                "+1 (555) 901-2345", "Business Administration", "1st Year", 3.25, "Active",
                "2006-04-18", "Male", "670 Walnut Dr, Los Angeles, CA",
                "Grace Kim (Mother) - +1 (555) 109-8765",
                "Freshman representative. Interested in technological entrepreneurship and venture capital."
            ),
            (
                "STU-2026-009", "Amara", "Okafor", "amara.okafor@university.edu",
                "+1 (555) 112-3344", "Data Science & Analytics", "3rd Year", 3.80, "Active",
                "2004-07-25", "Female", "244 Sunset Rd, Atlanta, GA",
                "Chidi Okafor (Father) - +1 (555) 998-8776",
                "Focus on Natural Language Processing and computational linguistics. Active student tutor."
            ),
            (
                "STU-2026-010", "Liam", "O'Connor", "liam.oconnor@university.edu",
                "+1 (555) 223-4455", "Mechanical Engineering", "2nd Year", 2.95, "Inactive",
                "2005-02-10", "Male", "150 Forest Crest, Portland, OR",
                "Patricia O'Connor (Mother) - +1 (555) 887-7665",
                "Currently on academic probation advisory review. Academic counseling support session scheduled."
            )
        ]

        cursor.executemany("""
            INSERT INTO students (
                student_id, first_name, last_name, email, phone,
                department, year_level, gpa, status, date_of_birth,
                gender, address, emergency_contact, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_students)
        conn.commit()
        return True


def generate_next_student_id():
    """Generate the next unique student ID formatted as STU-YYYY-NNN."""
    current_year = datetime.now().year
    prefix = f"STU-{current_year}-"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT student_id FROM students 
            WHERE student_id LIKE ? 
            ORDER BY id DESC LIMIT 1
        """, (f"{prefix}%",))
        row = cursor.fetchone()

        if row:
            try:
                last_number = int(row['student_id'].split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            cursor.execute("SELECT COUNT(*) as count FROM students")
            count = cursor.fetchone()['count']
            next_number = count + 1

        return f"{prefix}{next_number:03d}"


def get_all_students(search=None, department=None, status=None, sort_by='id', order='desc'):
    """Fetch students with optional filtering, searching, and sorting."""
    valid_sort_columns = {
        'id': 'id',
        'student_id': 'student_id',
        'name': 'first_name',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'department': 'department',
        'gpa': 'gpa',
        'status': 'status',
        'created_at': 'created_at'
    }
    sort_column = valid_sort_columns.get(sort_by, 'id')
    sort_order = 'ASC' if str(order).upper() == 'ASC' else 'DESC'

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search and search.strip():
        term = f"%{search.strip()}%"
        query += """ AND (
            first_name LIKE ? OR 
            last_name LIKE ? OR 
            student_id LIKE ? OR 
            email LIKE ? OR 
            department LIKE ? OR 
            phone LIKE ?
        )"""
        params.extend([term, term, term, term, term, term])

    if department and department.strip() and department.strip() != 'All':
        query += " AND department = ?"
        params.append(department.strip())

    if status and status.strip() and status.strip() != 'All':
        query += " AND status = ?"
        params.append(status.strip())

    query += f" ORDER BY {sort_column} {sort_order}"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_student_by_id(id_val):
    """Retrieve a single student by numeric ID or student_id string."""
    with get_db() as conn:
        cursor = conn.cursor()
        if str(id_val).isdigit():
            cursor.execute("SELECT * FROM students WHERE id = ?", (int(id_val),))
        else:
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (str(id_val),))
        row = cursor.fetchone()
        return dict(row) if row else None


def check_email_exists(email, exclude_id=None):
    """Check if an email is already registered, optionally excluding an existing student ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        if exclude_id is not None:
            cursor.execute("SELECT id FROM students WHERE LOWER(email) = LOWER(?) AND id != ?", (email, exclude_id))
        else:
            cursor.execute("SELECT id FROM students WHERE LOWER(email) = LOWER(?)", (email,))
        return cursor.fetchone() is not None


def check_student_id_exists(student_id, exclude_id=None):
    """Check if a student_id already exists."""
    with get_db() as conn:
        cursor = conn.cursor()
        if exclude_id is not None:
            cursor.execute("SELECT id FROM students WHERE UPPER(student_id) = UPPER(?) AND id != ?", (student_id, exclude_id))
        else:
            cursor.execute("SELECT id FROM students WHERE UPPER(student_id) = UPPER(?)", (student_id,))
        return cursor.fetchone() is not None


def create_student(data):
    """Insert a new student record into the database."""
    student_id = data.get('student_id')
    if not student_id or not student_id.strip():
        student_id = generate_next_student_id()
    else:
        student_id = student_id.strip().upper()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (
                student_id, first_name, last_name, email, phone,
                department, year_level, gpa, status, date_of_birth,
                gender, address, emergency_contact, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            data['first_name'].strip(),
            data['last_name'].strip(),
            data['email'].strip().lower(),
            data['phone'].strip(),
            data['department'].strip(),
            data['year_level'].strip(),
            float(data['gpa']),
            data.get('status', 'Active'),
            data.get('date_of_birth') or None,
            data.get('gender') or None,
            data.get('address') or None,
            data.get('emergency_contact') or None,
            data.get('notes') or None
        ))
        conn.commit()
        new_id = cursor.lastrowid

    return get_student_by_id(new_id)


def update_student(id_val, data):
    """Update an existing student record."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students SET
                student_id = ?,
                first_name = ?,
                last_name = ?,
                email = ?,
                phone = ?,
                department = ?,
                year_level = ?,
                gpa = ?,
                status = ?,
                date_of_birth = ?,
                gender = ?,
                address = ?,
                emergency_contact = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data['student_id'].strip().upper(),
            data['first_name'].strip(),
            data['last_name'].strip(),
            data['email'].strip().lower(),
            data['phone'].strip(),
            data['department'].strip(),
            data['year_level'].strip(),
            float(data['gpa']),
            data['status'],
            data.get('date_of_birth') or None,
            data.get('gender') or None,
            data.get('address') or None,
            data.get('emergency_contact') or None,
            data.get('notes') or None,
            int(id_val)
        ))
        conn.commit()

    return get_student_by_id(id_val)


def delete_student(id_val):
    """Delete a student record by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (int(id_val),))
        conn.commit()
        return cursor.rowcount > 0


def get_stats():
    """Retrieve statistical summary of the student body."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_students,
                ROUND(AVG(gpa), 2) as average_gpa,
                MAX(gpa) as highest_gpa,
                MIN(gpa) as lowest_gpa,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN status = 'On Leave' THEN 1 ELSE 0 END) as on_leave_count,
                SUM(CASE WHEN status = 'Graduated' THEN 1 ELSE 0 END) as graduated_count,
                SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inactive_count
            FROM students
        """)
        summary = dict(cursor.fetchone())

        cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM students 
            GROUP BY department 
            ORDER BY count DESC
        """)
        departments = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT year_level, COUNT(*) as count 
            FROM students 
            GROUP BY year_level 
            ORDER BY count DESC
        """)
        year_levels = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT COUNT(*) as count FROM students WHERE gpa >= 3.8")
        honor_roll_count = cursor.fetchone()['count']

        summary['honor_roll_count'] = honor_roll_count
        summary['department_breakdown'] = departments
        summary['year_level_breakdown'] = year_levels

        return summary
