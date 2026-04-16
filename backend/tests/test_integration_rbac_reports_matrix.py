def _login(api_client, username: str, password: str) -> str:
    status_code, payload = api_client(
        "POST",
        "/api/v1/auth/login",
        form_body={"username": username, "password": password},
    )
    assert status_code == 200, payload
    return payload["access_token"]


def test_reports_rbac_matrix(
    api_client,
    auth_token: str,
    seeded_entities: dict[str, str],
) -> None:
    doctor_token = _login(
        api_client,
        seeded_entities["doctor_username"],
        seeded_entities["doctor_password"],
    )
    registrar_token = _login(
        api_client,
        seeded_entities["registrar_username"],
        seeded_entities["registrar_password"],
    )

    date_from = "2026-01-01"
    date_to = "2026-12-31"
    endpoints = {
        "doctor_workload": f"/api/v1/reports/doctor-workload?date_from={date_from}&date_to={date_to}",
        "diagnoses": f"/api/v1/reports/diagnoses?date_from={date_from}&date_to={date_to}&limit=5",
        "appointments": f"/api/v1/reports/appointments?date_from={date_from}&date_to={date_to}",
        "finance": f"/api/v1/reports/finance?date_from={date_from}&date_to={date_to}",
    }

    for endpoint in endpoints.values():
        status_code, payload = api_client("GET", endpoint, token=auth_token)
        assert status_code == 200, payload

    status_code, payload = api_client("GET", endpoints["doctor_workload"], token=registrar_token)
    assert status_code == 200, payload
    status_code, payload = api_client("GET", endpoints["diagnoses"], token=registrar_token)
    assert status_code == 200, payload
    status_code, payload = api_client("GET", endpoints["appointments"], token=registrar_token)
    assert status_code == 200, payload
    status_code, payload = api_client("GET", endpoints["finance"], token=registrar_token)
    assert status_code == 403, payload

    status_code, payload = api_client("GET", endpoints["diagnoses"], token=doctor_token)
    assert status_code == 200, payload
    status_code, payload = api_client("GET", endpoints["doctor_workload"], token=doctor_token)
    assert status_code == 403, payload
    status_code, payload = api_client("GET", endpoints["appointments"], token=doctor_token)
    assert status_code == 403, payload
    status_code, payload = api_client("GET", endpoints["finance"], token=doctor_token)
    assert status_code == 403, payload
