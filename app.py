"""
Flask Application for Student Record Management System.
Provides RESTful APIs for CRUD operations and serves the web frontend.
"""

import io
import csv
import re
from flask import Flask, render_template, request, jsonify, Response
import database

app = Flask(__name__, static_folder='static', template_folder='templates')

# Email validation regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
VALID_STATUSES = ['Active', 'Inactive', 'On Leave', 'Graduated']
VALID_YEAR_LEVELS = ['1st Year', '2nd Year', '3rd Year', '4th Year', 'Masters', 'PhD']


@app.before_request
def setup_on_startup():
    """Ensure database schema is ready before handling requests."""
    # Ensure database is initialized
    database.init_db()
    database.seed_sample_data(force=False)


@app.route('/')
def index():
    """Serve the main SPA application page."""
    return render_template('index.html')


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Return aggregated metrics and statistics."""
    try:
        stats = database.get_stats()
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/students', methods=['GET'])
def list_students():
    """List students with search, filters, and sorting."""
    try:
        search = request.args.get('search', '').strip()
        department = request.args.get('department', '').strip()
        status = request.args.get('status', '').strip()
        sort_by = request.args.get('sort_by', 'id').strip()
        order = request.args.get('order', 'desc').strip()

        students = database.get_all_students(
            search=search if search else None,
            department=department if department else None,
            status=status if status else None,
            sort_by=sort_by,
            order=order
        )

        return jsonify({
            'success': True,
            'count': len(students),
            'data': students
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Retrieve details for a single student."""
    try:
        student = database.get_student_by_id(student_id)
        if not student:
            return jsonify({
                'success': False,
                'error': f'Student with ID {student_id} not found.'
            }), 404

        return jsonify({
            'success': True,
            'data': student
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/next-id', methods=['GET'])
def get_next_id():
    """Return the next suggested student ID."""
    try:
        next_id = database.generate_next_student_id()
        return jsonify({
            'success': True,
            'next_id': next_id
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def validate_student_payload(data, is_update=False, current_id=None):
    """Validate student record payload fields."""
    errors = {}

    first_name = data.get('first_name', '').strip()
    if not first_name:
        errors['first_name'] = 'First name is required.'
    elif len(first_name) < 2 or len(first_name) > 50:
        errors['first_name'] = 'First name must be between 2 and 50 characters.'

    last_name = data.get('last_name', '').strip()
    if not last_name:
        errors['last_name'] = 'Last name is required.'
    elif len(last_name) < 2 or len(last_name) > 50:
        errors['last_name'] = 'Last name must be between 2 and 50 characters.'

    email = data.get('email', '').strip().lower()
    if not email:
        errors['email'] = 'Email address is required.'
    elif not re.match(EMAIL_REGEX, email):
        errors['email'] = 'Invalid email address format.'
    elif database.check_email_exists(email, exclude_id=current_id):
        errors['email'] = f"The email '{email}' is already in use by another student."

    phone = data.get('phone', '').strip()
    if not phone:
        errors['phone'] = 'Phone number is required.'
    elif len(phone) < 7 or len(phone) > 25:
        errors['phone'] = 'Phone number must be between 7 and 25 characters.'

    department = data.get('department', '').strip()
    if not department:
        errors['department'] = 'Department is required.'

    year_level = data.get('year_level', '').strip()
    if not year_level:
        errors['year_level'] = 'Year level is required.'

    # GPA validation
    gpa_val = data.get('gpa')
    if gpa_val is None or str(gpa_val).strip() == '':
        errors['gpa'] = 'GPA is required.'
    else:
        try:
            gpa_float = float(gpa_val)
            if gpa_float < 0.0 or gpa_float > 4.0:
                errors['gpa'] = 'GPA must be between 0.00 and 4.00.'
        except (ValueError, TypeError):
            errors['gpa'] = 'GPA must be a valid numeric decimal (e.g., 3.75).'

    # Status validation
    status = data.get('status', 'Active').strip()
    if status not in VALID_STATUSES:
        errors['status'] = f"Status must be one of: {', '.join(VALID_STATUSES)}."

    # Student ID validation if provided
    student_id = data.get('student_id', '').strip()
    if student_id and database.check_student_id_exists(student_id, exclude_id=current_id):
        errors['student_id'] = f"Student ID '{student_id}' is already registered."

    return errors


@app.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request body (JSON expected).'
            }), 400

        errors = validate_student_payload(data, is_update=False)
        if errors:
            return jsonify({
                'success': False,
                'errors': errors,
                'error': 'Validation failed. Please correct the highlighted errors.'
            }), 422

        new_student = database.create_student(data)
        return jsonify({
            'success': True,
            'message': f"Student {new_student['first_name']} {new_student['last_name']} ({new_student['student_id']}) added successfully.",
            'data': new_student
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update an existing student record."""
    try:
        existing = database.get_student_by_id(student_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': f'Student with ID {student_id} not found.'
            }), 404

        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request body (JSON expected).'
            }), 400

        # Preserve student_id if not given
        if 'student_id' not in data or not data['student_id']:
            data['student_id'] = existing['student_id']

        errors = validate_student_payload(data, is_update=True, current_id=student_id)
        if errors:
            return jsonify({
                'success': False,
                'errors': errors,
                'error': 'Validation failed. Please correct the highlighted errors.'
            }), 422

        updated_student = database.update_student(student_id, data)
        return jsonify({
            'success': True,
            'message': f"Student {updated_student['first_name']} {updated_student['last_name']} updated successfully.",
            'data': updated_student
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student record."""
    try:
        existing = database.get_student_by_id(student_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': f'Student with ID {student_id} not found.'
            }), 404

        database.delete_student(student_id)
        return jsonify({
            'success': True,
            'message': f"Student {existing['first_name']} {existing['last_name']} ({existing['student_id']}) was successfully deleted.",
            'id': student_id
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/seed', methods=['POST'])
def reset_seed_data():
    """Reset database with initial demo data."""
    try:
        database.seed_sample_data(force=True)
        return jsonify({
            'success': True,
            'message': 'Sample data successfully restored!'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export student records to CSV format."""
    try:
        students = database.get_all_students()
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            'ID', 'Student ID', 'First Name', 'Last Name', 'Email',
            'Phone', 'Department', 'Year Level', 'GPA', 'Status',
            'Date of Birth', 'Gender', 'Address', 'Emergency Contact',
            'Notes', 'Created At'
        ]
        writer.writerow(headers)

        for s in students:
            writer.writerow([
                s['id'], s['student_id'], s['first_name'], s['last_name'],
                s['email'], s['phone'], s['department'], s['year_level'],
                s['gpa'], s['status'], s['date_of_birth'] or '',
                s['gender'] or '', s['address'] or '', s['emergency_contact'] or '',
                s['notes'] or '', s['created_at']
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=student_records.csv'}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    database.init_db()
    database.seed_sample_data(force=False)
    print("AcademicPulse Student Record System running at http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
