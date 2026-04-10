def test_health(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["code"] == "OK"
    assert body["data"]["status"] == "healthy"
    assert body["request_id"] is not None


def test_auth_required(client):
    response = client.get("/api/v1/trades/declarations?page_no=1&page_size=20")
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "AUTH_REQUIRED"


def test_whoami(client, user1001_headers):
    response = client.get("/api/v1/auth/whoami", headers=user1001_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["org_id"] == 1001
    assert body["data"]["is_admin"] is False


def test_login_and_whoami_with_jwt(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "user1001", "password": "pass1001"},
    )
    assert login_resp.status_code == 200
    login_body = login_resp.json()
    assert login_body["success"] is True
    token = login_body["data"]["access_token"]
    refresh_token = login_body["data"]["refresh_token"]
    assert token
    assert refresh_token

    whoami_resp = client.get(
        "/api/v1/auth/whoami",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert whoami_resp.status_code == 200
    whoami_body = whoami_resp.json()
    assert whoami_body["data"]["username"] == "user1001"
    assert whoami_body["data"]["org_id"] == 1001


def test_refresh_token_flow(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "user1001", "password": "pass1001"},
    )
    assert login_resp.status_code == 200
    first = login_resp.json()["data"]

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first["refresh_token"]},
    )
    assert refresh_resp.status_code == 200
    second = refresh_resp.json()["data"]
    assert second["access_token"] != first["access_token"]
    assert second["refresh_token"] != first["refresh_token"]

    old_refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first["refresh_token"]},
    )
    assert old_refresh_resp.status_code == 401
    assert old_refresh_resp.json()["code"] == "AUTH_REFRESH_INVALID"


def test_logout_revokes_refresh_token(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "user1001", "password": "pass1001"},
    )
    token = login_resp.json()["data"]["access_token"]
    refresh_token = login_resp.json()["data"]["refresh_token"]

    logout_resp = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_resp.status_code == 200
    assert logout_resp.json()["data"]["revoked"] is True

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401
    assert refresh_resp.json()["code"] == "AUTH_REFRESH_INVALID"


def test_login_failed(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "user1001", "password": "wrong-password"},
    )
    assert login_resp.status_code == 401
    body = login_resp.json()
    assert body["code"] == "AUTH_LOGIN_FAILED"


def test_register_then_login_with_password(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={"username": "reg_user_01", "password": "regpass01"},
    )
    assert reg.status_code == 200
    reg_body = reg.json()
    assert reg_body["success"] is True
    assert reg_body["data"]["username"] == "reg_user_01"
    token = reg_body["data"]["access_token"]
    assert token

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "Reg_User_01", "password": "regpass01"},
    )
    assert login_resp.status_code == 200
    assert login_resp.json()["data"]["username"] == "reg_user_01"

    whoami = client.get(
        "/api/v1/auth/whoami",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert whoami.status_code == 200
    assert whoami.json()["data"]["username"] == "reg_user_01"


def test_register_duplicate_username(client):
    u = "reg_user_dup"
    r1 = client.post("/api/v1/auth/register", json={"username": u, "password": "password01"})
    assert r1.status_code == 200
    r2 = client.post("/api/v1/auth/register", json={"username": u, "password": "password02"})
    assert r2.status_code == 409
    assert r2.json()["code"] == "AUTH_USERNAME_TAKEN"


def test_rule_query(client, user1001_headers):
    response = client.get(
        "/api/v1/rules?province_code=GD&trade_date=2026-04-09",
        headers=user1001_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["province_code"] == "GD"
    assert body["data"]["version"] == "2026.04"


def test_trade_declaration_create_and_query(client, user1001_headers):
    payload = {
        "province_code": "GD",
        "trade_date": "2026-04-09",
        "market_type": "SPOT_DA",
        "timeslots": [
            {"slot": "09:00-09:15", "volume_mwh": 12.5, "price": 420}
        ],
        "idempotency_key": "dec-20260409-001",
    }

    create_resp = client.post("/api/v1/trades/declarations", json=payload, headers=user1001_headers)
    assert create_resp.status_code == 200
    create_body = create_resp.json()
    declaration_id = create_body["data"]["declaration_id"]
    assert create_body["data"]["rule_version"] == "2026.04"
    assert create_body["data"]["duplicate"] is False

    dup_resp = client.post("/api/v1/trades/declarations", json=payload, headers=user1001_headers)
    assert dup_resp.status_code == 200
    dup_body = dup_resp.json()
    assert dup_body["data"]["declaration_id"] == declaration_id
    assert dup_body["data"]["duplicate"] is True

    get_resp = client.get(f"/api/v1/trades/declarations/{declaration_id}", headers=user1001_headers)
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["success"] is True
    assert get_body["data"]["declaration_id"] == declaration_id

    list_resp = client.get("/api/v1/trades/declarations?page_no=1&page_size=20", headers=user1001_headers)
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["data"]["total"] >= 1
    assert len(list_body["data"]["items"]) >= 1


def test_trade_declaration_not_found(client, user1001_headers):
    response = client.get("/api/v1/trades/declarations/DEC-UNKNOWN", headers=user1001_headers)
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "TRADE_DECLARATION_NOT_FOUND"


def test_trade_declaration_rule_validation(client, user1001_headers):
    payload = {
        "province_code": "GD",
        "trade_date": "2026-04-09",
        "market_type": "SPOT_DA",
        "timeslots": [
            {"slot": "09:00-09:15", "volume_mwh": 12.5, "price": 99999}
        ],
        "idempotency_key": "dec-20260409-invalid-001",
    }
    response = client.post("/api/v1/trades/declarations", json=payload, headers=user1001_headers)
    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "RULE_VALIDATION_ERROR"


def test_settlement_date_range_validation(client, user1001_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "cycle_start": "2026-04-10",
        "cycle_end": "2026-04-01",
    }
    response = client.post("/api/v1/settlement/reconcile/tasks", json=payload, headers=user1001_headers)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["code"] == "VALIDATION_ERROR"


def test_settlement_task_lifecycle(client, user1001_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "cycle_start": "2026-04-01",
        "cycle_end": "2026-04-08",
    }
    create_resp = client.post("/api/v1/settlement/reconcile/tasks", json=payload, headers=user1001_headers)
    assert create_resp.status_code == 200
    task_id = create_resp.json()["data"]["task_id"]

    get_resp = client.get(f"/api/v1/settlement/reconcile/tasks/{task_id}", headers=user1001_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["data"]["status"] == "queued"

    patch_running = client.patch(
        f"/api/v1/settlement/reconcile/tasks/{task_id}/status",
        json={"status": "running", "message": "start process"},
        headers=user1001_headers,
    )
    assert patch_running.status_code == 200
    assert patch_running.json()["data"]["status"] == "running"

    patch_completed = client.patch(
        f"/api/v1/settlement/reconcile/tasks/{task_id}/status",
        json={"status": "completed", "message": "done"},
        headers=user1001_headers,
    )
    assert patch_completed.status_code == 200
    assert patch_completed.json()["data"]["status"] == "completed"


def test_settlement_invalid_status_transition(client, user1001_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "cycle_start": "2026-04-01",
        "cycle_end": "2026-04-03",
    }
    create_resp = client.post("/api/v1/settlement/reconcile/tasks", json=payload, headers=user1001_headers)
    task_id = create_resp.json()["data"]["task_id"]

    response = client.patch(
        f"/api/v1/settlement/reconcile/tasks/{task_id}/status",
        json={"status": "completed"},
        headers=user1001_headers,
    )
    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "INVALID_STATUS_TRANSITION"


def test_risk_query(client, user1001_headers):
    response = client.get(
        "/api/v1/risk/deviation?trade_date=2026-04-09&org_id=1001&province_code=GD",
        headers=user1001_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["deviation_risk_level"] in {"low", "medium", "high"}
    assert body["data"]["rule_version"] == "2026.04"


def test_risk_cross_org_forbidden(client, user1001_headers):
    response = client.get(
        "/api/v1/risk/deviation?trade_date=2026-04-09&org_id=1002&province_code=GD",
        headers=user1001_headers,
    )
    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "FORBIDDEN"


def test_market_prices_query(client, user1001_headers):
    response = client.get(
        "/api/v1/market/prices?province_code=GD&page_no=1&page_size=20",
        headers=user1001_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True


def test_market_province_metrics(client, user1001_headers):
    response = client.get("/api/v1/market/province-metrics", headers=user1001_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    provinces = body["data"]["provinces"]
    assert isinstance(provinces, list)
    if provinces:
        row = provinces[0]
        assert "province_code" in row
        assert "avg_price" in row
        assert "market_date" in row


def test_cross_org_forbidden(client, user1001_headers, user1002_headers):
    payload = {
        "province_code": "GD",
        "trade_date": "2026-04-10",
        "market_type": "SPOT_DA",
        "timeslots": [{"slot": "09:00-09:15", "volume_mwh": 8, "price": 410}],
        "idempotency_key": "dec-20260410-org1-001",
    }
    create_resp = client.post("/api/v1/trades/declarations", json=payload, headers=user1001_headers)
    declaration_id = create_resp.json()["data"]["declaration_id"]

    forbidden_resp = client.get(
        f"/api/v1/trades/declarations/{declaration_id}",
        headers=user1002_headers,
    )
    assert forbidden_resp.status_code == 404


def test_admin_can_access_cross_org(client, user1001_headers, admin_headers):
    payload = {
        "province_code": "GD",
        "trade_date": "2026-04-11",
        "market_type": "SPOT_DA",
        "timeslots": [{"slot": "09:00-09:15", "volume_mwh": 9, "price": 411}],
        "idempotency_key": "dec-20260411-org1-001",
    }
    create_resp = client.post("/api/v1/trades/declarations", json=payload, headers=user1001_headers)
    declaration_id = create_resp.json()["data"]["declaration_id"]

    admin_resp = client.get(
        f"/api/v1/trades/declarations/{declaration_id}",
        headers=admin_headers,
    )
    assert admin_resp.status_code == 200
    assert admin_resp.json()["data"]["org_id"] == 1001


def test_audit_log_query(client, user1001_headers):
    response = client.get("/api/v1/audit/logs?page_no=1&page_size=20", headers=user1001_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
