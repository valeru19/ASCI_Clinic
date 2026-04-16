import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime, timedelta

import psycopg
import pytest


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_USERNAME = os.getenv("TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "admin12345")
DB_DSN = os.getenv("TEST_DB_DSN", "postgresql://clinic_user:clinic_pass@db:5432/clinic")


def _request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict | None = None,
    form_body: dict | None = None,
) -> tuple[int, dict]:
    url = f"{API_BASE_URL}{path}"
    headers: dict[str, str] = {}
    data: bytes | None = None

    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(json_body).encode("utf-8")
    elif form_body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = urllib.parse.urlencode(form_body).encode("utf-8")

    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            payload = response.read().decode("utf-8")
            return response.status, json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        try:
            body = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            body = {"raw": payload}
        return exc.code, body


@pytest.fixture(scope="session")
def db_conn() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(DB_DSN)
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(scope="session")
def auth_token() -> str:
    last_payload: dict = {}
    last_status = 0
    for _ in range(20):
        try:
            status_code, payload = _request(
                "POST",
                "/api/v1/auth/login",
                form_body={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            )
            if status_code == 200:
                return payload["access_token"]
            last_status = status_code
            last_payload = payload
        except urllib.error.URLError as exc:
            last_status = 0
            last_payload = {"error": str(exc)}
        time.sleep(0.5)

    assert last_status == 200, last_payload
    raise AssertionError("Unreachable")


@pytest.fixture(scope="session")
def seeded_entities(db_conn: psycopg.Connection) -> dict[str, str]:
    uid = str(uuid.uuid4())
    doctor_user_id = str(uuid.uuid4())
    registrar_user_id = str(uuid.uuid4())
    doctor_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())
    schedule_id = str(uuid.uuid4())
    slot_id = str(uuid.uuid4())
    slot_id_alt = str(uuid.uuid4())
    slot_id_validation = str(uuid.uuid4())
    medication_id = str(uuid.uuid4())
    test_type_id = str(uuid.uuid4())
    doctor_username = f"doctor_{uid[:8]}"
    doctor_password = "doctor12345"
    registrar_username = f"registrar_{uid[:8]}"
    registrar_password = "registrar12345"

    specialty_name = f"Integration Specialty {uid[:8]}"
    specialty_id = 0
    license_number = f"LIC-{uid[:10]}"
    icd10_code = f"Z{int(uid[0], 16) % 10}{int(uid[1], 16) % 10}.9"
    lab_test_code = f"TEST-{uid[:8]}"

    now = datetime.now(UTC)
    visit_day = now + timedelta(days=1)
    weekday = visit_day.isoweekday()
    start_time = visit_day.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(minutes=30)

    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO clinic.users (id, username, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), 'doctor', true)
            """,
            (
                doctor_user_id,
                doctor_username,
                f"{doctor_username}@clinic.local",
                doctor_password,
            ),
        )
        cur.execute(
            """
            INSERT INTO clinic.users (id, username, email, password_hash, role, is_active)
            VALUES (%s, %s, %s, crypt(%s, gen_salt('bf')), 'registrar', true)
            """,
            (
                registrar_user_id,
                registrar_username,
                f"{registrar_username}@clinic.local",
                registrar_password,
            ),
        )
        cur.execute(
            """
            INSERT INTO clinic.doctors (id, user_id, license_number, experience_years, is_active)
            VALUES (%s, %s, %s, 7, true)
            """,
            (doctor_id, doctor_user_id, license_number),
        )
        cur.execute(
            """
            INSERT INTO clinic.patients (id, last_name, first_name, birth_date, gender, is_active)
            VALUES (%s, %s, %s, %s, 'M', true)
            """,
            (patient_id, "Иванов", "Петр", date(1990, 1, 1)),
        )
        cur.execute(
            "INSERT INTO clinic.specialties (name) VALUES (%s) RETURNING id",
            (specialty_name,),
        )
        specialty_id = int(cur.fetchone()[0])
        cur.execute(
            """
            INSERT INTO clinic.schedules (id, doctor_id, weekday, start_time, end_time, slot_minutes, is_active)
            VALUES (%s, %s, %s, %s, %s, 30, true)
            """,
            (schedule_id, doctor_id, weekday, start_time.time(), (start_time + timedelta(hours=1)).time()),
        )
        cur.execute(
            """
            INSERT INTO clinic.schedule_slots (id, schedule_id, start_at, end_at, status)
            VALUES (%s, %s, %s, %s, 'available')
            """,
            (slot_id, schedule_id, start_time, end_time),
        )
        cur.execute(
            """
            INSERT INTO clinic.schedule_slots (id, schedule_id, start_at, end_at, status)
            VALUES (%s, %s, %s, %s, 'available')
            """,
            (slot_id_alt, schedule_id, end_time, end_time + timedelta(minutes=30)),
        )
        cur.execute(
            """
            INSERT INTO clinic.schedule_slots (id, schedule_id, start_at, end_at, status)
            VALUES (%s, %s, %s, %s, 'available')
            """,
            (
                slot_id_validation,
                schedule_id,
                end_time + timedelta(minutes=30),
                end_time + timedelta(minutes=60),
            ),
        )
        cur.execute(
            "INSERT INTO clinic.icd10_codes (code, title) VALUES (%s, %s)",
            (icd10_code, "Integration diagnosis"),
        )
        cur.execute(
            """
            INSERT INTO clinic.medications (id, name, form, strength, atc_code)
            VALUES (%s, %s, 'tablet', '500 mg', %s)
            """,
            (medication_id, f"Medication {uid[:8]}", f"ATC-{uid[:6]}"),
        )
        cur.execute(
            """
            INSERT INTO clinic.lab_test_types (id, code, name, unit, reference_range)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (test_type_id, lab_test_code, f"Test {uid[:8]}", "mmol/L", "3.9-5.5"),
        )
        cur.execute(
            """
            INSERT INTO clinic.invoices (id, patient_id, status, total_amount, issued_at)
            VALUES (%s, %s, 'paid', 1500.00, now())
            """,
            (str(uuid.uuid4()), patient_id),
        )

    return {
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "slot_id": slot_id,
        "slot_id_alt": slot_id_alt,
        "slot_id_validation": slot_id_validation,
        "icd10_code": icd10_code,
        "medication_id": medication_id,
        "specialty_id": str(specialty_id),
        "test_type_id": test_type_id,
        "doctor_username": doctor_username,
        "doctor_password": doctor_password,
        "registrar_username": registrar_username,
        "registrar_password": registrar_password,
    }


@pytest.fixture(scope="session")
def api_client() -> callable:
    return _request
