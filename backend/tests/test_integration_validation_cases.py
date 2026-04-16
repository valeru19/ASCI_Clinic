def test_validation_errors_return_422(
    api_client,
    auth_token: str,
    seeded_entities: dict[str, str],
) -> None:
    status_code, appointment = api_client(
        "POST",
        "/api/v1/appointments/",
        token=auth_token,
        json_body={
            "patient_id": seeded_entities["patient_id"],
            "doctor_id": seeded_entities["doctor_id"],
            "slot_id": seeded_entities["slot_id_validation"],
            "reason": "Сценарий валидации",
        },
    )
    assert status_code == 201, appointment
    appointment_id = appointment["id"]

    status_code, visit = api_client(
        "POST",
        "/api/v1/visits/",
        token=auth_token,
        json_body={
            "appointment_id": appointment_id,
            "chief_complaint": "Тест валидации",
            "exam_notes": "Тест валидации",
        },
    )
    assert status_code == 201, visit
    visit_id = visit["id"]

    status_code, invalid_diagnosis = api_client(
        "POST",
        f"/api/v1/visits/{visit_id}/diagnoses",
        token=auth_token,
        json_body={
            "items": [
                {
                    "icd10_code": "BAD-CODE",
                    "is_primary": True,
                }
            ]
        },
    )
    assert status_code == 422, invalid_diagnosis

    status_code, invalid_prescription = api_client(
        "POST",
        f"/api/v1/visits/{visit_id}/prescriptions",
        token=auth_token,
        json_body={
            "items": [
                {
                    "medication_id": seeded_entities["medication_id"],
                    "dosage": "five hundred mg",
                    "frequency": "2 раза в день",
                    "duration_days": 5,
                }
            ]
        },
    )
    assert status_code == 422, invalid_prescription

    status_code, invalid_referral = api_client(
        "POST",
        f"/api/v1/visits/{visit_id}/referrals",
        token=auth_token,
        json_body={
            "items": [
                {
                    "target_specialty_id": 0,
                    "reason": "Некорректная специальность",
                }
            ]
        },
    )
    assert status_code == 422, invalid_referral

    status_code, order = api_client(
        "POST",
        "/api/v1/labs/orders",
        token=auth_token,
        json_body={"visit_id": visit_id},
    )
    assert status_code == 201, order
    order_id = order["id"]

    status_code, order_items = api_client(
        "POST",
        f"/api/v1/labs/orders/{order_id}/items",
        token=auth_token,
        json_body={
            "items": [{"test_type_id": seeded_entities["test_type_id"], "priority": "normal"}]
        },
    )
    assert status_code == 201, order_items
    order_item_id = order_items["items"][0]["id"]

    status_code, invalid_result = api_client(
        "POST",
        "/api/v1/labs/results",
        token=auth_token,
        json_body={
            "lab_order_item_id": order_item_id,
            "flag": "normal",
            "validated_by_doctor_id": seeded_entities["doctor_id"],
        },
    )
    assert status_code == 422, invalid_result

    status_code, invalid_report_limit = api_client(
        "GET",
        "/api/v1/reports/diagnoses?date_from=2026-01-01&date_to=2026-12-31&limit=0",
        token=auth_token,
    )
    assert status_code == 422, invalid_report_limit
