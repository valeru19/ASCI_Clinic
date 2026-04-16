from datetime import UTC, datetime, timedelta


def test_schedule_period_boundaries(
    api_client,
    auth_token: str,
    seeded_entities: dict[str, str],
) -> None:
    target_day = (datetime.now(UTC) + timedelta(days=3)).date()
    weekday = target_day.isoweekday()

    status_code, schedule = api_client(
        "POST",
        "/api/v1/schedules/",
        token=auth_token,
        json_body={
            "doctor_id": seeded_entities["doctor_id"],
            "weekday": weekday,
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "slot_minutes": 30,
            "is_active": True,
        },
    )
    assert status_code == 201, schedule
    schedule_id = schedule["id"]

    status_code, generated = api_client(
        "POST",
        "/api/v1/schedule-slots/generate",
        token=auth_token,
        json_body={
            "schedule_id": schedule_id,
            "date_from": target_day.isoformat(),
            "date_to": target_day.isoformat(),
        },
    )
    assert status_code == 201, generated
    assert generated["created"] == 2, generated
    assert len(generated["slots"]) == 2, generated

    for slot in generated["slots"]:
        assert slot["start_at"].startswith(target_day.isoformat()), slot
        assert slot["end_at"].startswith(target_day.isoformat()), slot


def test_period_validation_errors_return_422(
    api_client,
    auth_token: str,
    seeded_entities: dict[str, str],
) -> None:
    status_code, schedule = api_client(
        "POST",
        "/api/v1/schedules/",
        token=auth_token,
        json_body={
            "doctor_id": seeded_entities["doctor_id"],
            "weekday": 1,
            "start_time": "16:00:00",
            "end_time": "17:00:00",
            "slot_minutes": 30,
            "is_active": True,
        },
    )
    assert status_code == 201, schedule
    schedule_id = schedule["id"]

    status_code, invalid_generate = api_client(
        "POST",
        "/api/v1/schedule-slots/generate",
        token=auth_token,
        json_body={
            "schedule_id": schedule_id,
            "date_from": "2026-06-10",
            "date_to": "2026-06-01",
        },
    )
    assert status_code == 422, invalid_generate

    status_code, invalid_exception = api_client(
        "POST",
        "/api/v1/schedule-exceptions/",
        token=auth_token,
        json_body={
            "doctor_id": seeded_entities["doctor_id"],
            "date_from": "2026-07-20",
            "date_to": "2026-07-10",
            "reason": "Проверка границ диапазона дат",
        },
    )
    assert status_code == 422, invalid_exception


def test_reports_single_day_period_is_supported(
    api_client,
    auth_token: str,
) -> None:
    today = datetime.now(UTC).date().isoformat()

    status_code, diagnoses = api_client(
        "GET",
        f"/api/v1/reports/diagnoses?date_from={today}&date_to={today}&limit=1",
        token=auth_token,
    )
    assert status_code == 200, diagnoses
    assert diagnoses["date_from"] == today, diagnoses
    assert diagnoses["date_to"] == today, diagnoses
    assert len(diagnoses["items"]) <= 1, diagnoses

    status_code, appointments = api_client(
        "GET",
        f"/api/v1/reports/appointments?date_from={today}&date_to={today}",
        token=auth_token,
    )
    assert status_code == 200, appointments
    assert appointments["date_from"] == today, appointments
    assert appointments["date_to"] == today, appointments
    assert appointments["total"] >= 0, appointments
