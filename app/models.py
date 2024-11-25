import json
import os

COURSES_FILE = 'courses.json'  # This should be in the root of your Flask project

class Course:
    def __init__(self, department, course_number, course_name, syllabus_filename):
        self.department = department
        self.course_number = course_number
        self.course_name = course_name
        self.syllabus_filename = syllabus_filename

    def to_dict(self):
        return {
            'department': self.department,
            'course_number': self.course_number,
            'course_name': self.course_name,
            'syllabus_filename': self.syllabus_filename
        }

def load_courses():
    if os.path.exists(COURSES_FILE):
        with open(COURSES_FILE, 'r') as file:
            courses_data = json.load(file)
            return [Course(**course) for course in courses_data]
    return []

def save_courses(courses):
    with open(COURSES_FILE, 'w') as file:
        json.dump([course.to_dict() for course in courses], file)
