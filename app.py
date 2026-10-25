"""
Doctor Appointment Booking Web Application
Built with Python Flask and SQLite for CI/CD demonstration.
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g

# Initialize Flask application
app = Flask(__name__)

# Secret key required for flashing alert messages and session management
app.secret_key = os.environ.get("SECRET_KEY", "doctor-appointment-secret-key-12345")

# Predefined list of doctors as specified in project requirements
DOCTORS = [
    "Dr. Sharma (Cardiology)",
    "Dr. Patil (Dermatology)",
    "Dr. Khan (Pediatrics)",
    "Dr. Joshi (General)",
]

# Predefined list of available time slots
TIME_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "14:00",
    "15:00",
    "16:00",
]


def get_db_path():
    """
    Get the SQLite database file path.
    Defaults to 'appointments.db', configurable via the DB_PATH environment variable.
    """
    return os.environ.get("DB_PATH", "appointments.db")


def init_db():
    """
    Create the appointments table if it does not already exist.
    Enforces a UNIQUE constraint on (doctor, date, time_slot) to prevent double booking.
    """
    db_path = get_db_path()
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(doctor, date, time_slot)
        )
        """
    )
    conn.commit()
    conn.close()


def get_db():
    """
    Get or create an active SQLite database connection for the current Flask request context.
    Row factory is set to sqlite3.Row for dict-like column access.
    """
    if "db" not in g:
        init_db()  # Ensure table is initialized for current DB_PATH
        g.db = sqlite3.connect(get_db_path())
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    """Close the database connection when the request finishes."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Home page route:
    - GET: displays the booking form and the table of all booked appointments.
    - POST: validates and creates a new appointment, preventing double booking.
    """
    db = get_db()

    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        doctor = request.form.get("doctor", "").strip()
        date = request.form.get("date", "").strip()
        time_slot = request.form.get("time_slot", "").strip()

        # Validate that all required fields are provided
        if not patient_name or not doctor or not date or not time_slot:
            flash("Please fill in all fields to book an appointment.", "error")
            return redirect(url_for("index"))

        # Explicit check for duplicate booking (same doctor + date + time_slot)
        existing = db.execute(
            "SELECT id FROM appointments WHERE doctor = ? AND date = ? AND time_slot = ?",
            (doctor, date, time_slot),
        ).fetchone()

        if existing:
            flash("Sorry, that slot is already booked.", "error")
            return redirect(url_for("index"))

        # Insert new appointment; integrity error also catches race conditions
        try:
            db.execute(
                "INSERT INTO appointments (patient_name, doctor, date, time_slot) VALUES (?, ?, ?, ?)",
                (patient_name, doctor, date, time_slot),
            )
            db.commit()
            flash("Appointment booked successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Sorry, that slot is already booked.", "error")

        return redirect(url_for("index"))

    # GET request: fetch all appointments ordered by date and time
    cursor = db.execute(
        "SELECT id, patient_name, doctor, date, time_slot FROM appointments ORDER BY date ASC, time_slot ASC, id ASC"
    )
    appointments = cursor.fetchall()

    return render_template(
        "index.html",
        appointments=appointments,
        doctors=DOCTORS,
        time_slots=TIME_SLOTS,
    )


@app.route("/cancel/<int:appointment_id>", methods=["POST"])
def cancel(appointment_id):
    """
    Cancel an appointment by ID and remove it from the database.
    """
    db = get_db()
    db.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    db.commit()
    flash("Appointment cancelled successfully.", "info")
    return redirect(url_for("index"))


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint for Kubernetes liveness and readiness probes.
    Returns HTTP 200 with JSON status 'ok'.
    """
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    init_db()
    # Listen on host 0.0.0.0 and port 5000 as required for containerization
    app.run(host="0.0.0.0", port=5000, debug=False)
