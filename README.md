# CodeCraftHub Learning Management System

A beginner-friendly course-tracking REST API built with Python, Flask, and a JSON file. It is designed for learning basic REST API development.

## Features

- Create, list, retrieve, update, and delete courses (CRUD).
- Store course data in `courses.json`; no database is required.
- Automatically create the JSON file when the application starts.
- Validate required fields, dates, and course status values.
- Return JSON error messages for invalid input and missing courses.
- No authentication or user management.

## Course fields

Every course contains:

- `id`: automatically generated integer.
- `name`: required non-empty string.
- `description`: required non-empty string.
- `target_date`: required date in `YYYY-MM-DD` format.
- `status`: `Not Started`, `In Progress`, or `Completed`.
- `created_at`: automatically generated UTC timestamp.

## Project structure

```text
codecrafthub/
├── app.py
├── courses.json          # created automatically on first run
├── requirements.txt
├── README.md
└── tests/
    └── test_app.py
```

## Requirements

- Python 3.9 or later
- pip

## Installation on Windows

1. Extract the project ZIP file.
2. Open the `codecrafthub` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. (Recommended) Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, you can skip activation and use `python -m pip` commands below.

5. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

## Run the API

```powershell
python app.py
```

The API will be available at `http://127.0.0.1:5000`. Keep this terminal open while testing.

## API endpoints

| Method | Endpoint | Purpose | Success status |
|---|---|---|---|
| `POST` | `/api/courses` | Create a course | `201 Created` |
| `GET` | `/api/courses` | List all courses | `200 OK` |
| `GET` | `/api/courses/<course_id>` | Retrieve one course | `200 OK` |
| `PUT` | `/api/courses/<course_id>` | Replace a course's editable fields | `200 OK` |
| `DELETE` | `/api/courses/<course_id>` | Delete a course | `200 OK` |

### Create a course

Open a **second terminal** while the server is running:

```powershell
curl.exe -X POST http://127.0.0.1:5000/api/courses -H "Content-Type: application/json" -d "{\"name\":\"Python Basics\",\"description\":\"Learn Python fundamentals\",\"target_date\":\"2027-01-31\",\"status\":\"Not Started\"}"
```

A successful response returns the course as JSON, including its generated `id` and `created_at`.

### List all courses

```powershell
curl.exe http://127.0.0.1:5000/api/courses
```

### Retrieve one course

```powershell
curl.exe http://127.0.0.1:5000/api/courses/1
```

Use the actual ID returned when creating the course.

### Update a course

`PUT` requires all four editable fields: `name`, `description`, `target_date`, and `status`.

```powershell
curl.exe -X PUT http://127.0.0.1:5000/api/courses/1 -H "Content-Type: application/json" -d "{\"name\":\"Python Basics\",\"description\":\"Learn Python and build small projects\",\"target_date\":\"2027-02-28\",\"status\":\"In Progress\"}"
```

### Delete a course

```powershell
curl.exe -X DELETE http://127.0.0.1:5000/api/courses/1
```

### Error examples

A request missing required fields returns `400 Bad Request`. A status other than the three allowed values returns `400 Bad Request`. An invalid date returns `400 Bad Request`. An unknown course ID returns `404 Not Found`. JSON file access or parsing failures return `500 Internal Server Error`.

Example request for a missing course:

```powershell
curl.exe -i http://127.0.0.1:5000/api/courses/999
```

## Automated tests

Install the dependencies, then run:

```powershell
python -m unittest discover -s tests -v
```

The tests use Flask's test client and a temporary JSON file, so they do not change your actual `courses.json`.

## Troubleshooting

- **`python` is not recognized:** try `py app.py` and `py -m pip install -r requirements.txt`.
- **Flask module not found:** run `python -m pip install -r requirements.txt` using the same Python interpreter used to run the app.
- **Port 5000 is already in use:** stop the other server or change the port at the bottom of `app.py`.
- **Course not found:** use the actual `id` returned by a successful `POST` request.
- **JSON parsing error:** check that `courses.json` contains a valid JSON list, such as `[]`.

## Notes

This is a small educational project. A JSON file is suitable for a simple lab, but it is not designed for concurrent writes or production-scale use. Flask's debug mode is for local development only.
