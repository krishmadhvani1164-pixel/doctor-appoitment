# Doctor Appointment System (doctor-appointment)

A lightweight, clean web application for doctor appointment scheduling built with **Python Flask** and **SQLite**. Designed specifically for college CI/CD pipeline demonstrations (Jenkins, Docker, and Kubernetes).

---

## Features

1. **Appointment Booking**: Schedule appointments with patient name, doctor selection, appointment date, and time slot.
2. **Predefined Doctors**:
   - Dr. Sharma (Cardiology)
   - Dr. Patil (Dermatology)
   - Dr. Khan (Pediatrics)
   - Dr. Joshi (General)
3. **Available Time Slots**: 09:00, 10:00, 11:00, 14:00, 15:00, 16:00.
4. **Double-Booking Prevention**: Automatically blocks duplicate bookings for the same doctor, date, and time slot. Displays a red alert message: *"Sorry, that slot is already booked."*
5. **Manage & Cancel Appointments**: Real-time table listing all confirmed appointments with a single-click cancel button.
6. **Kubernetes Health Check (`/health`)**: Lightweight JSON endpoint (`{"status": "ok"}`) for Kubernetes liveness and readiness probes.
7. **Version Display for CI/CD Demo**: Prominently shows **"Version 1"** in the top navigation header. Change this to **"Version 2"** in `templates/index.html` to showcase automated rollouts and zero-downtime updates in Kubernetes!
8. **Professional UI**: Clean blue header, white card layout, modern typography, responsive table, and clear alert feedback using Jinja templates and CSS.

---

## Project Structure

```text
doctor-appointment/
├── app.py                 # Flask application logic & SQLite database operations
├── test_app.py            # Automated test suite using pytest & Flask test client
├── requirements.txt       # Python dependencies (Flask, pytest)
├── Dockerfile             # Multi-step layer-cached container image definition
├── .dockerignore          # Excludes unneeded files from Docker builds
├── .gitignore             # Excludes databases, cache, and virtual environments
├── README.md              # Project documentation & run guide
├── templates/
│   └── index.html         # Jinja HTML template with Version 1 badge & UI cards
└── static/
    └── style.css          # CSS styles (blue header, cards, responsive table)
```

---

## 1. How to Run Locally

### Prerequisites
- Python 3.10+ installed

### Step-by-Step Setup

1. **Navigate to the project directory**:
   ```bash
   cd doctor-appointment
   ```

2. **(Optional) Create and activate a virtual environment**:
   ```bash
   # On Windows:
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask application**:
   ```bash
   python app.py
   ```

5. **Open in your browser**:
   Visit [http://localhost:5000](http://localhost:5000)

> **Environment Variables**:
> - `DB_PATH`: Set custom path for SQLite database (Default: `appointments.db`).
>   - Example: `export DB_PATH=/tmp/custom.db` (Linux/Mac) or `$env:DB_PATH="custom.db"` (PowerShell).

---

## 2. How to Run Automated Tests

The project includes unit and integration tests covering:
- Home page loading (`HTTP 200` and version string check)
- Successful appointment booking
- Prevention of double bookings (with exact error text verification)
- `/health` probe verification (`{"status": "ok"}`)
- Appointment cancellation

Run all tests using:
```bash
pytest
```

Or for detailed test execution output:
```bash
pytest -v
```

---

## 3. How to Build and Run with Docker

The application is containerized using an optimized, lightweight `python:3.11-slim` base image.

### Build the Docker Image
```bash
docker build -t doctor-appointment .
```

### Run the Container
```bash
docker run -p 5000:5000 doctor-appointment
```

Access the application at [http://localhost:5000](http://localhost:5000) and test the health check at [http://localhost:5000/health](http://localhost:5000/health).

---

## Viva & CI/CD Pipeline Reference Guide

| Topic | Explanation for Viva |
| :--- | :--- |
| **Jenkins** | In a Jenkins pipeline (`Jenkinsfile`), `pytest` is executed in a test stage before building the Docker image. If any test fails, the build halts immediately. |
| **Docker** | Layer caching is optimized in the `Dockerfile` by copying and installing `requirements.txt` before copying the source code, accelerating pipeline execution. |
| **Kubernetes** | The `/health` endpoint is configured in Kubernetes deployment YAML as `livenessProbe` and `readinessProbe` with `path: /health` and `port: 5000`. |
| **Zero Downtime Demo** | Change `"Version 1"` to `"Version 2"` in `templates/index.html`, commit to Git, and watch Jenkins trigger a rolling update in Kubernetes with zero downtime. |
| **Database Concurrency** | SQLite enforces a composite `UNIQUE(doctor, date, time_slot)` constraint at the schema level in addition to application-level checks, guaranteeing integrity. |
