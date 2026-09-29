# AcademiaPulse &mdash; Student Records Management System

A modern, high-performance full-stack application for managing institutional student records, academic performance, and enrollments. Built with a responsive glassmorphic frontend, a Python Flask RESTful backend, and a robust SQLite relational database.

---

## 🌟 Key Features

1. **Add Students**:
   - Complete enrollment registration form with real-time field validation.
   - Dual GPA input (smooth slider & numeric decimal input).
   - Auto-generated institutional Student IDs (`STU-YYYY-NNN`).
   - Detailed sections for basic info, academic program, contact, emergency details, and advisory notes.

2. **Update Records**:
   - In-place modal editor with pre-populated student information.
   - Server-side and client-side duplicate email & student ID validation.
   - Automatic `updated_at` timestamp tracking.

3. **Delete Records**:
   - Safe delete dialog with explicit confirmation naming the target student and ID.
   - Real-time removal and roster metric recalculation.

4. **View Student Details**:
   - Student Profile Dossier with honors tier badge (Summa Cum Laude, Dean's List, etc.).
   - Comprehensive academic, contact, emergency, and advisory records.
   - One-click print / PDF export capability.

5. **Live Search, Filter & Sort**:
   - Instant search across Student Name, ID, Email, Department, and Phone with keyboard shortcut (`/`).
   - Department dropdown filter & status filter pills (Active, On Leave, Graduated, Inactive).
   - Sort by Name, GPA, or Student ID.
   - Dual layout switch: **Interactive Data Table** or **Responsive Profile Cards Grid**.

6. **Analytics & KPI Dashboard**:
   - Total Enrolled Students count with intake rate.
   - Active Students count and roster percentage.
   - Institutional Average GPA meter with Dean's Honor Roll count.
   - Academic Departments distribution.

7. **Theme & UX Enhancements**:
   - Seamless **Dark Mode** (default) and **Light Mode** toggle saved to `localStorage`.
   - Floating animated toast notification system for feedback.
   - CSV export endpoint for records backup.
   - Demo sample dataset reset option.

---

## 🛠️ Technology Stack

- **Frontend**: Vanilla HTML5, CSS3 (Custom Glassmorphism Design System, CSS Variables, Responsive Grid/Flexbox), Vanilla JavaScript (ES6+ SPA architecture, Fetch API).
- **Backend**: Python 3, Flask 3.1.
- **Database**: SQLite 3 (WAL mode, relational constraints, indexed search).
- **Typography & Icons**: Google Fonts (*Plus Jakarta Sans*, *JetBrains Mono*), Font Awesome 6.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+ (Standard library includes `sqlite3`)
- `pip install -r requirements.txt`

### 2. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Run Automated Tests
```bash
python -m unittest tests/test_api.py
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/students` | List students (supports `search`, `department`, `status`, `sort_by`, `order`) |
| `GET` | `/api/students/<id>` | Retrieve full details of a student by numeric ID |
| `POST` | `/api/students` | Enroll a new student record (JSON body) |
| `PUT` | `/api/students/<id>` | Update an existing student record (JSON body) |
| `DELETE` | `/api/students/<id>` | Delete a student record by ID |
| `GET` | `/api/stats` | Retrieve aggregated student body metrics and KPIs |
| `GET` | `/api/next-id` | Retrieve the next suggested unique Student ID |
| `GET` | `/api/export/csv` | Download all student records in CSV format |
| `POST` | `/api/seed` | Restore initial sample demo dataset |

---

## 📁 Project Structure

```
AsfyStdntMsy/
├── app.py                # Flask server, route definitions & API endpoints
├── database.py           # SQLite connection manager, schema initialization & CRUD queries
├── schema.sql            # SQL schema with constraints and performance indexes
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Design system, glassmorphism, responsive layouts, animations
│   ├── js/
│   │   └── app.js        # SPA client controller, state management, API calls & toasts
│   └── favicon.svg       # SVG logo favicon
├── templates/
│   └── index.html        # Semantic HTML5 Single Page Application dashboard
└── tests/
    └── test_api.py       # 12 automated unit and integration tests
```
