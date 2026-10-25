"""
Unit and integration tests for the Doctor Appointment web application.
Uses Flask's test client with a clean temporary SQLite database per test.
"""

import os
import pytest
from app import app, init_db


@pytest.fixture
def client(tmp_path):
    """
    Pytest fixture that creates an isolated SQLite database in a temporary directory
    and provides a Flask test client for HTTP requests.
    """
    test_db = str(tmp_path / "test_appointments.db")
    os.environ["DB_PATH"] = test_db
    app.config["TESTING"] = True

    # Initialize the temporary test database schema
    init_db()

    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


def test_home_page_loads(client):
    """
    Requirement 1 & 7: Verify home page loads with HTTP 200 and displays 'Version 1'.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Version 1" in response.data
    assert b"Doctor Appointment System" in response.data
    assert b"Book an Appointment" in response.data


def test_booking_works(client):
    """
    Requirement 1, 2, 3, 4: Verify that a patient can successfully book an appointment.
    """
    booking_data = {
        "patient_name": "Alice Smith",
        "doctor": "Dr. Sharma (Cardiology)",
        "date": "2026-11-01",
        "time_slot": "10:00",
    }
    response = client.post("/", data=booking_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Appointment booked successfully!" in response.data
    assert b"Alice Smith" in response.data
    assert b"Dr. Sharma (Cardiology)" in response.data
    assert b"10:00" in response.data


def test_double_booking_blocked(client):
    """
    Requirement 5: Verify that the same doctor + date + slot cannot be booked twice,
    and returns the exact red error message: 'Sorry, that slot is already booked.'
    """
    first_booking = {
        "patient_name": "Alice Smith",
        "doctor": "Dr. Sharma (Cardiology)",
        "date": "2026-11-01",
        "time_slot": "10:00",
    }
    # First booking succeeds
    res1 = client.post("/", data=first_booking, follow_redirects=True)
    assert res1.status_code == 200
    assert b"Appointment booked successfully!" in res1.data

    # Attempt second booking with identical doctor, date, and time_slot
    second_booking = {
        "patient_name": "Bob Jones",
        "doctor": "Dr. Sharma (Cardiology)",
        "date": "2026-11-01",
        "time_slot": "10:00",
    }
    res2 = client.post("/", data=second_booking, follow_redirects=True)
    assert res2.status_code == 200
    assert b"Sorry, that slot is already booked." in res2.data
    # Ensure Bob Jones was not added
    assert b"Bob Jones" not in res2.data


def test_health_check(client):
    """
    Requirement 6: Verify /health route returns HTTP 200 and {'status': 'ok'}
    for Kubernetes liveness/readiness probes.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"status": "ok"}


def test_cancel_appointment(client):
    """
    Requirement 4: Verify that an appointment can be cancelled via POST /cancel/<id>.
    """
    booking_data = {
        "patient_name": "Charlie Brown",
        "doctor": "Dr. Patil (Dermatology)",
        "date": "2026-11-02",
        "time_slot": "11:00",
    }
    client.post("/", data=booking_data, follow_redirects=True)

    # Cancel the appointment (id=1 in fresh DB)
    response = client.post("/cancel/1", follow_redirects=True)
    assert response.status_code == 200
    assert b"Appointment cancelled successfully." in response.data
    assert b"Charlie Brown" not in response.data
