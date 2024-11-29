import pytest
from flask import Flask
from app import create_app
from app.models import load_courses, save_courses, Course
import os
from io import BytesIO

# Define the syllabus folder path
SYLLABUS_FOLDER = r"C:\Users\sekha\OneDrive\Desktop\Syllabus Chatbot using Retrieval Augmented Generation\syllabus_files"

# Setup the Flask app for testing
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    app.config['SYLLABUS_FOLDER'] = SYLLABUS_FOLDER
    os.makedirs(SYLLABUS_FOLDER, exist_ok=True)  # Ensure syllabus folder exists
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

    # Debugging: Print the actual HTML for reference
    print("\n=== Debugging: Response Data ===")
    print(response.data.decode())

    # Adjust the assertion to match the actual header in the template
    assert b'<h1>Student Dashboard</h1>' in response.data

# Test for viewing a syllabus
def test_view_syllabus(client):
    # Simulating the existence of a PDF syllabus file
    syllabus_content = b'%PDF-1.4\n%Test Syllabus Content\n'
    syllabus_path = os.path.join(SYLLABUS_FOLDER, 'cs101.pdf')
    with open(syllabus_path, 'wb') as f:
        f.write(syllabus_content)

    response = client.get('/syllabus/cs101.pdf')
    assert response.status_code == 200
    assert b'%PDF' in response.data

    response.close()  # Ensure the file handle is released
    os.remove(syllabus_path)  # Cleanup

# Test for professor login (valid credentials)
def test_professor_login_valid(client):
    response = client.post('/login', data={
        'email': 'dr.fu@uco.edu',
        'password': 'Spring@1'
    })
    assert response.status_code == 302  # Should redirect to professor dashboard
    assert '/professor_dashboard' in response.location

# Test for deleting a course
def test_professor_delete_course(client):
    # Add a course
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
    response = client.get('/delete_course/0', follow_redirects=True)
    assert response.status_code == 200
    assert b'Course deleted successfully!' in response.data

# Test for adding a course
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
    }, content_type='multipart/form-data')

    assert response.status_code == 200
    assert b'Course added successfully!' in response.data
