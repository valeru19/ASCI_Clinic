from datetime import date, timedelta


def test_full_clinical_and_reporting_flow(api_client, auth_token: str, seeded_entities: dict[str, str]) -> None:
    status_code, appointment = api_client(
        "POST",
        "/api/v1/appointments/",
        token=auth_token,
        json_body={
            "patient_id": seeded_entities["patient_id"],
            "doctor_id": seeded_entities["doctor_id"],
            "slot_id": seeded_entities["slot_id"],
            "reason": "Интеграционный тестовый прием",
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
            "chief_complaint": "Головная боль",
            "exam_notes": "Состояние удовлетворительное",
            "treatment_plan": "Наблюдение",
        },
    )
    assert status_code == 201, visit
    visit_id = visit["id"]

    status_code, diagnoses = api_client(
        "POST",
        f"/api/v1/visits/{visit_id}/diagnoses",
        token=auth_token,
        json_body={
            "items": [
                {
                    "icd10_code": seeded_entities["icd10_code"],
                    "is_primary": True,
                    "comment": "Первичный диагноз",
                }
            ]
        },
    )
    assert status_code == 201, diagnoses
    assert diagnoses["created"] == 1

    status_code, prescriptions = api_client(
        "POST",
        f"/api/v1/visits/{visit_id}/prescriptions",
        token=auth_token,
        json_body={
            "items": [
                {
                    "medication_id": seeded_entities["medication_id"],
                    "dosage": "500 mg",
                    "frequency": "2 раза в день",
                    "duration_days": 5,
                    "instructions": "После еды",
                }
            ]
        },
    )
    assert status_code == 201, prescriptions
    assert prescriptions["created"] == 1

    status_code, referrals = api_client(
        "POST",
        f"/api/v1/visits/{visit_id}/referrals",
        token=auth_token,
        json_body={
            "items": [
                {
                    "target_specialty_id": int(seeded_entities["specialty_id"]),
                    "target_doctor_id": seeded_entities["doctor_id"],
                    "reason": "Дополнительная консультация",
                }
            ]
        },
    )
    assert status_code == 201, referrals
    assert referrals["created"] == 1

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
            "items": [{"test_type_id": seeded_entities["test_type_id"], "priority": "urgent"}]
        },
    )
    assert status_code == 201, order_items
    order_item_id = order_items["items"][0]["id"]

    status_code, lab_result = api_client(
        "POST",
        "/api/v1/labs/results",
        token=auth_token,
        json_body={
            "lab_order_item_id": order_item_id,
            "value_numeric": 5.2,
            "unit": "mmol/L",
            "reference_range": "3.9-5.5",
            "flag": "normal",
            "validated_by_doctor_id": seeded_entities["doctor_id"],
        },
    )
    assert status_code == 201, lab_result

    date_from = (date.today() - timedelta(days=2)).isoformat()
    date_to = (date.today() + timedelta(days=2)).isoformat()

    status_code, report_workload = api_client(
        "GET",
        f"/api/v1/reports/doctor-workload?date_from={date_from}&date_to={date_to}",
        token=auth_token,
    )
    assert status_code == 200, report_workload
    assert len(report_workload["items"]) >= 1

    status_code, report_diagnoses = api_client(
        "GET",
        f"/api/v1/reports/diagnoses?date_from={date_from}&date_to={date_to}&limit=10",
        token=auth_token,
    )
    assert status_code == 200, report_diagnoses
    assert any(item["icd10_code"] == seeded_entities["icd10_code"] for item in report_diagnoses["items"])

    status_code, report_appointments = api_client(
        "GET",
        f"/api/v1/reports/appointments?date_from={date_from}&date_to={date_to}",
        token=auth_token,
    )
    assert status_code == 200, report_appointments
    assert report_appointments["total"] >= 1

    status_code, report_finance = api_client(
        "GET",
        f"/api/v1/reports/finance?date_from={date_from}&date_to={date_to}",
        token=auth_token,
    )
    assert status_code == 200, report_finance
    assert report_finance["invoices_count"] >= 1
