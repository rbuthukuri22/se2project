from flask import Blueprint, render_template, redirect, url_for, request, session, flash, send_from_directory 
from .models import Course, load_courses, save_courses
import os

main = Blueprint('main', __name__)

# Define the absolute path for the syllabus files
UPLOAD_FOLDER = r'C:\Users\sekha\OneDrive\Desktop\Syllabus Chatbot using Retrieval Augmented Generation\syllabus_files'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PROFESSORS = {
    "dr.fu@uco.edu": "Spring@1",
    "dr,qian@uco.edu": "Summer@1",
    "m@uco.edu": "Fall@1",
    "dr.lee@uco.edu": "music@3",
    "dr.walker@uco.edu": "science@1",
    "dr.sri@uco.edu": "math@4",
    "manasa@uco.edu": "arts@3",
}

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email in PROFESSORS and PROFESSORS[email] == password:
            session["professor"] = email
            return redirect(url_for("main.professor_dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@main.route("/professor_dashboard", methods=["GET", "POST"])
def professor_dashboard():
    if "professor" not in session:
        return redirect(url_for("main.login"))

    courses = load_courses()  # Load courses from the JSON file

    if request.method == "POST":
        department = request.form["department"]
        course_number = request.form["course_number"]
        course_name = request.form["course_name"]
        syllabus = request.files["syllabus"]

        if syllabus and syllabus.filename.endswith(".pdf"):
            syllabus_path = os.path.join(UPLOAD_FOLDER, syllabus.filename)
            syllabus.save(syllabus_path)

            new_course = Course(department, course_number, course_name, syllabus.filename)
            courses.append(new_course)
            save_courses(courses)  # Save courses back to the JSON file
            flash("Course added successfully!")
        else:
            flash("Invalid syllabus file. Only PDF format is allowed.")

    return render_template("professor_dashboard.html", courses=courses, enumerate=enumerate)

@main.route("/delete_course/<int:course_id>")
def delete_course(course_id):
    if "professor" not in session:
        return redirect(url_for("main.login"))

    courses = load_courses()  # Load courses from the JSON file
    if 0 <= course_id < len(courses):
        del courses[course_id]
        save_courses(courses)  # Save the updated course list back to JSON
        flash("Course deleted successfully!")
    else:
        flash("Invalid course ID.")

    return redirect(url_for("main.professor_dashboard"))

@main.route("/syllabus/<filename>")
def view_syllabus(filename):
    # Construct the full path to the syllabus file
    syllabus_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(syllabus_path):
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        flash("Syllabus not found!")
        return redirect(url_for('main.professor_dashboard'))

@main.route("/logout")
def logout():
    session.pop("professor", None)
    return redirect(url_for("main.home"))

# Student Dashboard Route (for searching courses)
@main.route("/student_dashboard", methods=["GET", "POST"])
def student_dashboard():
    # Load all courses
    courses = load_courses()

    # If search parameters are provided
    search_results = courses
    if request.method == "POST":
        department = request.form.get("department", "").lower()
        course_number = request.form.get("course_number", "").lower()
        course_name = request.form.get("course_name", "").lower()

        # Filter courses based on search parameters
        search_results = [
            course for course in courses
            if department in course.department.lower() and
            course_number in course.course_number.lower() and
            course_name in course.course_name.lower()
        ]

    return render_template("student_dashboard.html", courses=search_results)
