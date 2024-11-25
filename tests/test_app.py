import pytest
from flask import Flask
from app import create_app
from app.models import load_courses, save_courses, Course
import os
from io import BytesIO

# Setup the Flask app for testing
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    app.config['SYLLABUS_FOLDER'] = 'syllabus_files'  # Temporary folder for syllabus files
    # Ensure the test syllabus folder exists
    os.makedirs(app.config['SYLLABUS_FOLDER'], exist_ok=True)
    with app.test_client() as client:
        yield client

# Test for the home route
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Syllabus Chatbot' in response.data

# Test for the student dashboard (GET request)
def test_student_dashboard_get(client):
    response = client.get('/student_dashboard')
    assert response.status_code == 200
    assert b'Search Courses' in response.data

# Test for searching courses in the student dashboard (POST request)
def test_student_dashboard_search(client):
    # Prepare some test data
    courses = [
        Course('CS', '101', 'Introduction to Computer Science', 'cs101.pdf'),
        Course('MATH', '201', 'Calculus I', 'calculus.pdf')
    ]
    save_courses(courses)

    # Simulate a search for CS courses
    response = client.post('/student_dashboard', data={
        'department': 'CS',
        'course_number': '',
        'course_name': ''
    })
    
    assert response.status_code == 200
    assert b'Introduction to Computer Science' in response.data

# Test for viewing a syllabus
def test_view_syllabus(client):
    # Simulating the existence of a PDF syllabus file in the folder
    syllabus_content = b'%PDF-1.4\n%Test Syllabus Content\n'
    syllabus_path = os.path.join('syllabus_files', 'cs101.pdf')
    with open(syllabus_path, 'wb') as f:
        f.write(syllabus_content)
    
    response = client.get('/syllabus/cs101.pdf')
    assert response.status_code == 200
    assert b'%PDF' in response.data  # Checking if it's a PDF file

    # Clean up the test syllabus file
    os.remove(syllabus_path)

# Test for professor login (valid credentials)
def test_professor_login_valid(client):
    response = client.post('/login', data={
        'email': 'dr.fu@uco.edu',
        'password': 'Spring@1'
    })
    assert response.status_code == 302  # Should redirect to professor dashboard
    assert response.location == '/professor_dashboard'

# Test for professor login (invalid credentials)
def test_professor_login_invalid(client):
    response = client.post('/login', data={
        'email': 'invalid@uco.edu',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # Should return to login page
    assert b'Invalid credentials' in response.data

# Test for professor adding a course (POST request)
def test_professor_add_course(client):
    # Simulate professor login
    client.post('/login', data={
        'email': 'dr.fu@uco.edu',
        'password': 'Spring@1'
    })

    # Simulate adding a new course with a mock file
    syllabus_file = (BytesIO(b'%PDF-1.4\n%Mock PDF Syllabus Content\n'), 'test_syllabus.pdf')

    response = client.post('/professor_dashboard', data={
        'department': 'CS',
        'course_number': '303',
        'course_name': 'Data Structures',
        'syllabus': syllabus_file
    })
    
    assert response.status_code == 200
    assert b'Course added successfully!' in response.data

# Test for deleting a course
def test_professor_delete_course(client):
    # Add a course first
    courses = load_courses()
    new_course = Course('CS', '404', 'Algorithms', 'algorithms.pdf')
    courses.append(new_course)
    save_courses(courses)

    # Simulate professor login
    client.post('/login', data={
        'email': 'dr.fu@uco.edu',
        'password': 'Spring@1'
    })

    # Simulate deleting the course
    response = client.get('/delete_course/0')
    assert response.status_code == 302  # Should redirect
    assert b'Course deleted successfully!' in response.data
