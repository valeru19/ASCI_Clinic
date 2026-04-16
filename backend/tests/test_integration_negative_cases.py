def test_doctor_forbidden_to_create_patient(api_client, seeded_entities: dict[str, str]) -> None:
    status_code, doctor_login = api_client(
        "POST",
        "/api/v1/auth/login",
        form_body={
            "username": seeded_entities["doctor_username"],
            "password": seeded_entities["doctor_password"],
        },
    )
    assert status_code == 200, doctor_login
    doctor_token = doctor_login["access_token"]

    status_code, response = api_client(
        "POST",
        "/api/v1/patients/",
        token=doctor_token,
        json_body={
            "last_name": "Тестов",
            "first_name": "Доктор",
            "birth_date": "1995-05-10",
            "gender": "M",
        },
    )
    assert status_code == 403, response


def test_duplicate_lab_result_returns_conflict(
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
            "slot_id": seeded_entities["slot_id_alt"],
            "reason": "Негативный интеграционный сценарий",
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
            "chief_complaint": "Слабость",
            "exam_notes": "Без особенностей",
        },
    )
    assert status_code == 201, visit
    visit_id = visit["id"]

    status_code, lab_order = api_client(
        "POST",
        "/api/v1/labs/orders",
        token=auth_token,
        json_body={"visit_id": visit_id},
    )
    assert status_code == 201, lab_order
    order_id = lab_order["id"]

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

    payload = {
        "lab_order_item_id": order_item_id,
        "value_numeric": 4.8,
        "unit": "mmol/L",
        "reference_range": "3.9-5.5",
        "flag": "normal",
        "validated_by_doctor_id": seeded_entities["doctor_id"],
    }
    status_code, first_result = api_client(
        "POST",
        "/api/v1/labs/results",
        token=auth_token,
        json_body=payload,
    )
    assert status_code == 201, first_result

    status_code, second_result = api_client(
        "POST",
        "/api/v1/labs/results",
        token=auth_token,
        json_body=payload,
    )
    assert status_code == 409, second_result
