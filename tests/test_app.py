"""Automated tests for CodeCraftHub, using a temporary JSON file."""

import json
import tempfile
import unittest
from pathlib import Path

import app as codecrafthub


class CodeCraftHubTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_file = codecrafthub.COURSES_FILE
        codecrafthub.COURSES_FILE = Path(self.temp_dir.name) / "courses.json"
        codecrafthub.app.config["TESTING"] = True
        self.client = codecrafthub.app.test_client()

    def tearDown(self):
        codecrafthub.COURSES_FILE = self.original_file
        self.temp_dir.cleanup()

    def payload(self, **overrides):
        data = {
            "name": "Python Basics",
            "description": "Learn Python fundamentals",
            "target_date": "2027-01-31",
            "status": "Not Started",
        }
        data.update(overrides)
        return data

    def test_get_courses_starts_empty_and_creates_file(self):
        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])
        self.assertTrue(codecrafthub.COURSES_FILE.exists())

    def test_create_course(self):
        response = self.client.post("/api/courses", json=self.payload())
        self.assertEqual(response.status_code, 201)
        course = response.get_json()
        self.assertEqual(course["id"], 1)
        self.assertEqual(course["name"], "Python Basics")
        self.assertIn("created_at", course)

    def test_get_specific_course(self):
        created = self.client.post("/api/courses", json=self.payload()).get_json()
        response = self.client.get(f"/api/courses/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["id"], created["id"])

    def test_update_course(self):
        created = self.client.post("/api/courses", json=self.payload()).get_json()
        updated = self.payload(status="In Progress", name="Updated Python")
        response = self.client.put(f"/api/courses/{created['id']}", json=updated)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "In Progress")
        self.assertEqual(response.get_json()["name"], "Updated Python")

    def test_delete_course(self):
        created = self.client.post("/api/courses", json=self.payload()).get_json()
        response = self.client.delete(f"/api/courses/{created['id']}")
        self.assertEqual(response.status_code, 200)
        missing = self.client.get(f"/api/courses/{created['id']}")
        self.assertEqual(missing.status_code, 404)

    def test_missing_fields_are_rejected(self):
        response = self.client.post("/api/courses", json={"name": "Incomplete"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required field", response.get_json()["error"])

    def test_invalid_status_is_rejected(self):
        response = self.client.post("/api/courses", json=self.payload(status="Pending"))
        self.assertEqual(response.status_code, 400)

    def test_invalid_date_is_rejected(self):
        response = self.client.post("/api/courses", json=self.payload(target_date="2027-02-30"))
        self.assertEqual(response.status_code, 400)

    def test_nonexistent_course_returns_404(self):
        response = self.client.get("/api/courses/999")
        self.assertEqual(response.status_code, 404)

    def test_data_persists_in_json_file(self):
        self.client.post("/api/courses", json=self.payload())
        data = json.loads(codecrafthub.COURSES_FILE.read_text(encoding="utf-8"))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Python Basics")


if __name__ == "__main__":
    unittest.main()
