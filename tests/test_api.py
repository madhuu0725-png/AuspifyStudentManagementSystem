"""
Unit and integration tests for Student Record Management System API.
Tests all CRUD operations, filtering, sorting, validation, and analytics.
"""

import json
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app
import database


class StudentAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client and reset sample database."""
        self.app = app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            database.init_db()
            database.seed_sample_data(force=True)

    def test_01_get_stats(self):
        """Test retrieving dashboard statistics."""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['data']['total_students'], 10)
        self.assertIn('average_gpa', data['data'])
        self.assertIn('department_breakdown', data['data'])

    def test_02_get_all_students(self):
        """Test retrieving student list."""
        response = self.client.get('/api/students')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 10)
        self.assertIsInstance(data['data'], list)

    def test_03_search_students(self):
        """Test search query matching first name or student_id."""
        response = self.client.get('/api/students?search=Aria')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['data'][0]['first_name'], 'Aria')

    def test_04_filter_students_by_department_and_status(self):
        """Test department and status filters."""
        response = self.client.get('/api/students?department=Computer+Science+%26+AI&status=Active')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        for s in data['data']:
            self.assertEqual(s['department'], 'Computer Science & AI')
            self.assertEqual(s['status'], 'Active')

    def test_05_get_student_details_success(self):
        """Test fetching a single student by numeric ID."""
        list_resp = self.client.get('/api/students')
        all_students = json.loads(list_resp.data)['data']
        first_student = all_students[0]

        response = self.client.get(f"/api/students/{first_student['id']}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], first_student['id'])
        self.assertEqual(data['data']['student_id'], first_student['student_id'])

    def test_06_get_student_details_not_found(self):
        """Test fetching non-existent student returns 404."""
        response = self.client.get('/api/students/99999')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    def test_07_create_student_success(self):
        """Test creating a new student with valid payload."""
        payload = {
            "first_name": "Maya",
            "last_name": "Lin",
            "email": "maya.lin@university.edu",
            "phone": "+1 (555) 321-9988",
            "department": "Artificial Intelligence",
            "year_level": "1st Year",
            "gpa": 3.89,
            "status": "Active",
            "date_of_birth": "2006-05-15",
            "gender": "Female",
            "address": "404 Innovation Blvd, Seattle, WA",
            "emergency_contact": "Robert Lin (Father) - +1 (555) 998-1122",
            "notes": "Dean's scholar finalist"
        }
        response = self.client.post('/api/students',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['first_name'], 'Maya')
        self.assertEqual(data['data']['last_name'], 'Lin')
        self.assertTrue(data['data']['student_id'].startswith('STU-'))

    def test_08_create_student_validation_failure(self):
        """Test creating a student with invalid/missing fields returns 422."""
        payload = {
            "first_name": "",
            "last_name": "Test",
            "email": "invalid-email-string",
            "phone": "123",
            "department": "",
            "year_level": "",
            "gpa": 5.5,  # GPA exceeds 4.0
            "status": "InvalidStatus"
        }
        response = self.client.post('/api/students',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('first_name', data['errors'])
        self.assertIn('email', data['errors'])
        self.assertIn('gpa', data['errors'])
        self.assertIn('status', data['errors'])

    def test_09_create_student_duplicate_email(self):
        """Test creating a student with an already registered email."""
        payload = {
            "first_name": "Clone",
            "last_name": "Montgomery",
            "email": "aria.montgomery@university.edu",  # Already in sample data
            "phone": "+1 (555) 234-5678",
            "department": "Computer Science & AI",
            "year_level": "1st Year",
            "gpa": 3.50,
            "status": "Active"
        }
        response = self.client.post('/api/students',
                                   data=json.dumps(payload),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.data)
        self.assertIn('email', data['errors'])

    def test_10_update_student_success(self):
        """Test updating an existing student's information."""
        list_resp = self.client.get('/api/students')
        all_students = json.loads(list_resp.data)['data']
        target_student = all_students[1]

        payload = {
            "student_id": target_student['student_id'],
            "first_name": target_student['first_name'],
            "last_name": target_student['last_name'],
            "email": "updated.email@university.edu",
            "phone": "+1 (555) 345-6789",
            "department": target_student['department'],
            "year_level": target_student['year_level'],
            "gpa": 3.96,  # Promoted GPA
            "status": "Graduated",
            "notes": "Published honors thesis."
        }
        response = self.client.put(f"/api/students/{target_student['id']}",
                                  data=json.dumps(payload),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['gpa'], 3.96)
        self.assertEqual(data['data']['status'], 'Graduated')
        self.assertEqual(data['data']['email'], 'updated.email@university.edu')

    def test_11_delete_student_success(self):
        """Test deleting a student."""
        list_resp = self.client.get('/api/students')
        all_students = json.loads(list_resp.data)['data']
        student_to_delete = all_students[-1]
        target_id = student_to_delete['id']

        # Delete student
        response = self.client.delete(f"/api/students/{target_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # Verify it no longer exists
        verify_resp = self.client.get(f"/api/students/{target_id}")
        self.assertEqual(verify_resp.status_code, 404)

    def test_12_export_csv(self):
        """Test CSV export endpoint."""
        response = self.client.get('/api/export/csv')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn(b'Student ID,First Name,Last Name', response.data)


if __name__ == '__main__':
    unittest.main()
