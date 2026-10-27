"""
CodeCraftHub Learning Management System
A beginner-friendly Flask REST API that stores course data in courses.json.
"""

from datetime import datetime, timezone
import json
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

# Keep the JSON data file beside this app.py file.
COURSES_FILE = Path(__file__).resolve().parent / "courses.json"
ALLOWED_STATUSES = {"Not Started", "In Progress", "Completed"}


class StorageError(Exception):
    """Raised when course data cannot be read or written."""


def create_empty_courses_file():
    """Create courses.json with an empty list if it does not exist."""
    if not COURSES_FILE.exists():
        try:
            COURSES_FILE.write_text("[]", encoding="utf-8")
        except OSError as exc:
            raise StorageError("Unable to create courses.json.") from exc


def load_courses():
    """Read all courses from the JSON file."""
    create_empty_courses_file()
    try:
        with COURSES_FILE.open("r", encoding="utf-8") as file:
            courses = json.load(file)
    except json.JSONDecodeError as exc:
        raise StorageError("courses.json contains invalid JSON.") from exc
    except OSError as exc:
        raise StorageError("Unable to read courses.json.") from exc

    if not isinstance(courses, list):
        raise StorageError("courses.json must contain a JSON list.")
    return courses


def save_courses(courses):
    """Write all courses to the JSON file."""
    try:
        with COURSES_FILE.open("w", encoding="utf-8") as file:
            json.dump(courses, file, indent=2, ensure_ascii=False)
    except (OSError, TypeError) as exc:
        raise StorageError("Unable to write to courses.json.") from exc


def get_next_course_id(courses):
    """Return 1 for the first course, otherwise one more than the largest ID."""
    valid_ids = [
        course["id"]
        for course in courses
        if isinstance(course, dict)
        and isinstance(course.get("id"), int)
        and not isinstance(course.get("id"), bool)
    ]
    return max(valid_ids, default=0) + 1


def current_timestamp():
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_course_data(data):
    """Return an error message for invalid course input, or None if valid."""
    if not isinstance(data, dict):
        return "Request body must be a JSON object."

    required = ["name", "description", "target_date", "status"]
    missing = [field for field in required if field not in data]
    if missing:
        return "Missing required field(s): " + ", ".join(missing)

    if not isinstance(data["name"], str) or not data["name"].strip():
        return "The name field must be a non-empty string."

    if not isinstance(data["description"], str) or not data["description"].strip():
        return "The description field must be a non-empty string."

    if not isinstance(data["target_date"], str):
        return "The target_date field must use YYYY-MM-DD format."

    try:
        parsed_date = datetime.strptime(data["target_date"], "%Y-%m-%d")
        # Ensure strict YYYY-MM-DD representation.
        if parsed_date.strftime("%Y-%m-%d") != data["target_date"]:
            raise ValueError
    except ValueError:
        return "The target_date field must use YYYY-MM-DD format."

    if data["status"] not in ALLOWED_STATUSES:
        return 'Invalid status. Use "Not Started", "In Progress", or "Completed".'

    return None


def find_course(courses, course_id):
    """Find a course by ID, returning None when it is not present."""
    return next((course for course in courses if course.get("id") == course_id), None)


@app.errorhandler(StorageError)
def handle_storage_error(error):
    return jsonify({"error": str(error)}), 500


@app.errorhandler(404)
def handle_unknown_route(error):
    return jsonify({"error": "The requested endpoint was not found."}), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return jsonify({"error": "The HTTP method is not allowed for this endpoint."}), 405


@app.route("/api/courses", methods=["POST"])
def create_course():
    """Create a course."""
    data = request.get_json(silent=True)
    error = validate_course_data(data)
    if error:
        return jsonify({"error": error}), 400

    courses = load_courses()
    course = {
        "id": get_next_course_id(courses),
        "name": data["name"].strip(),
        "description": data["description"].strip(),
        "target_date": data["target_date"],
        "status": data["status"],
        "created_at": current_timestamp(),
    }
    courses.append(course)
    save_courses(courses)
    return jsonify(course), 201


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Return all courses."""
    courses = load_courses()
    return jsonify(courses), 200


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """Return one course by ID."""
    course = find_course(load_courses(), course_id)
    if course is None:
        return jsonify({"error": f"Course with ID {course_id} was not found."}), 404
    return jsonify(course), 200


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """Replace the editable fields of an existing course."""
    data = request.get_json(silent=True)
    error = validate_course_data(data)
    if error:
        return jsonify({"error": error}), 400

    courses = load_courses()
    course = find_course(courses, course_id)
    if course is None:
        return jsonify({"error": f"Course with ID {course_id} was not found."}), 404

    course.update({
        "name": data["name"].strip(),
        "description": data["description"].strip(),
        "target_date": data["target_date"],
        "status": data["status"],
    })
    save_courses(courses)
    return jsonify(course), 200


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course by ID."""
    courses = load_courses()
    course = find_course(courses, course_id)
    if course is None:
        return jsonify({"error": f"Course with ID {course_id} was not found."}), 404

    courses.remove(course)
    save_courses(courses)
    return jsonify({"message": f"Course with ID {course_id} was deleted successfully."}), 200


if __name__ == "__main__":
    create_empty_courses_file()
    print("CodeCraftHub API is starting...")
    print(f"Data file: {COURSES_FILE}")
    print("API URL: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
