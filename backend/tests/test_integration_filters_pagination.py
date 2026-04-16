import uuid
from datetime import UTC, datetime, timedelta

import psycopg


def test_patients_search_and_pagination(
    api_client,
    auth_token: str,
) -> None:
    suffix = uuid.uuid4().hex[:8]
    patient_last_name = f"Pagination{suffix}"

    status_code, first_patient = api_client(
        "POST",
        "/api/v1/patients/",
        token=auth_token,
        json_body={
            "last_name": patient_last_name,
            "first_name": "Alpha",
            "birth_date": "1991-01-01",
            "gender": "M",
        },
    )
    assert status_code == 201, first_patient

    status_code, second_patient = api_client(
        "POST",
        "/api/v1/patients/",
        token=auth_token,
        json_body={
            "last_name": patient_last_name,
            "first_name": "Beta",
            "birth_date": "1992-02-02",
            "gender": "F",
        },
    )
    assert status_code == 201, second_patient

    status_code, page_1 = api_client(
        "GET",
        f"/api/v1/patients/?q={patient_last_name}&skip=0&limit=1",
        token=auth_token,
    )
    assert status_code == 200, page_1
    assert page_1["total"] >= 2, page_1
    assert len(page_1["items"]) == 1, page_1

    status_code, page_2 = api_client(
        "GET",
        f"/api/v1/patients/?q={patient_last_name}&skip=1&limit=1",
        token=auth_token,
    )
    assert status_code == 200, page_2
    assert page_2["total"] >= 2, page_2
    assert len(page_2["items"]) == 1, page_2
    assert page_1["items"][0]["id"] != page_2["items"][0]["id"]

    status_code, invalid_limit = api_client(
        "GET",
        f"/api/v1/patients/?q={patient_last_name}&limit=0",
        token=auth_token,
    )
    assert status_code == 422, invalid_limit


def test_appointments_filters_and_pagination(
    api_client,
    auth_token: str,
    seeded_entities: dict[str, str],
    db_conn: psycopg.Connection,
) -> None:
    schedule_id = str(uuid.uuid4())
    slot_1_id = str(uuid.uuid4())
    slot_2_id = str(uuid.uuid4())

    start_at = (datetime.now(UTC) + timedelta(days=5)).replace(
        hour=10,
        minute=0,
        second=0,
        microsecond=0,
    )

    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO clinic.schedules (id, doctor_id, weekday, start_time, end_time, slot_minutes, is_active)
            VALUES (%s, %s, %s, %s, %s, 30, true)
            """,
            (
                schedule_id,
                seeded_entities["doctor_id"],
                start_at.isoweekday(),
                start_at.time(),
                (start_at + timedelta(hours=1)).time(),
            ),
        )
        cur.execute(
            """
            INSERT INTO clinic.schedule_slots (id, schedule_id, start_at, end_at, status)
            VALUES (%s, %s, %s, %s, 'available')
            """,
            (slot_1_id, schedule_id, start_at, start_at + timedelta(minutes=30)),
        )
        cur.execute(
            """
            INSERT INTO clinic.schedule_slots (id, schedule_id, start_at, end_at, status)
            VALUES (%s, %s, %s, %s, 'available')
            """,
            (
                slot_2_id,
                schedule_id,
                start_at + timedelta(minutes=30),
                start_at + timedelta(minutes=60),
            ),
        )

    status_code, first_appointment = api_client(
        "POST",
        "/api/v1/appointments/",
        token=auth_token,
        json_body={
            "patient_id": seeded_entities["patient_id"],
            "doctor_id": seeded_entities["doctor_id"],
            "slot_id": slot_1_id,
            "reason": "Pagination flow #1",
        },
    )
    assert status_code == 201, first_appointment

    status_code, second_appointment = api_client(
        "POST",
        "/api/v1/appointments/",
        token=auth_token,
        json_body={
            "patient_id": seeded_entities["patient_id"],
            "doctor_id": seeded_entities["doctor_id"],
            "slot_id": slot_2_id,
            "reason": "Pagination flow #2",
        },
    )
    assert status_code == 201, second_appointment

    status_code, cancelled = api_client(
        "PATCH",
        f"/api/v1/appointments/{first_appointment['id']}/cancel",
        token=auth_token,
        json_body={"reason": "Cancel for filter check"},
    )
    assert status_code == 200, cancelled
    assert cancelled["status"] == "cancelled", cancelled

    status_code, planned_only = api_client(
        "GET",
        (
            f"/api/v1/appointments/?patient_id={seeded_entities['patient_id']}"
            "&status=planned&skip=0&limit=1"
        ),
        token=auth_token,
    )
    assert status_code == 200, planned_only
    assert planned_only["total"] >= 1, planned_only
    assert len(planned_only["items"]) == 1, planned_only
    assert planned_only["items"][0]["status"] == "planned", planned_only

    status_code, cancelled_only = api_client(
        "GET",
        (
            f"/api/v1/appointments/?patient_id={seeded_entities['patient_id']}"
            "&status=cancelled&skip=0&limit=5"
        ),
        token=auth_token,
    )
    assert status_code == 200, cancelled_only
    assert cancelled_only["total"] >= 1, cancelled_only
    assert cancelled_only["items"][0]["status"] == "cancelled", cancelled_only

    status_code, invalid_limit = api_client(
        "GET",
        "/api/v1/appointments/?limit=0",
        token=auth_token,
    )
    assert status_code == 422, invalid_limit
