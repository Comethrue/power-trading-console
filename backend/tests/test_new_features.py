"""合同台账、结算汇总、风险计算改进的补充测试用例。"""


# ── 合同台账 ──────────────────────────────────────────────

def test_contract_create_and_query(client, user1001_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "contract_type": "MEDIUM_LONG",
        "counterpart": "南方电网",
        "volume_mwh": 5000.0,
        "price": 450.0,
        "start_date": "2026-04-01",
        "end_date": "2026-04-30",
        "remark": "测试合同",
    }
    create_resp = client.post("/api/v1/contracts/contracts", json=payload, headers=user1001_headers)
    assert create_resp.status_code == 200
    body = create_resp.json()
    assert body["success"] is True
    contract_id = body["data"]["contract_id"]
    assert contract_id.startswith("CTR-")
    assert body["data"]["status"] == "active"

    get_resp = client.get(f"/api/v1/contracts/contracts/{contract_id}", headers=user1001_headers)
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["data"]["contract_id"] == contract_id
    assert get_body["data"]["volume_mwh"] == 5000.0
    assert get_body["data"]["counterpart"] == "南方电网"

    list_resp = client.get("/api/v1/contracts/contracts?page_no=1&page_size=20", headers=user1001_headers)
    assert list_resp.status_code == 200
    list_body = list_resp.json()
    assert list_body["data"]["total"] >= 1


def test_contract_filter_by_status(client, user1001_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "contract_type": "SPOT_DA",
        "volume_mwh": 100.0,
        "price": 380.0,
        "start_date": "2026-04-01",
        "end_date": "2026-04-10",
    }
    create_resp = client.post("/api/v1/contracts/contracts", json=payload, headers=user1001_headers)
    contract_id = create_resp.json()["data"]["contract_id"]

    # 按 active 过滤
    active_resp = client.get(
        "/api/v1/contracts/contracts?status=active&page_no=1&page_size=20",
        headers=user1001_headers,
    )
    assert active_resp.status_code == 200
    active_ids = [item["contract_id"] for item in active_resp.json()["data"]["items"]]
    assert contract_id in active_ids


def test_contract_status_update(client, user1001_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "contract_type": "SPOT_RT",
        "volume_mwh": 200.0,
        "price": 400.0,
        "start_date": "2026-04-01",
        "end_date": "2026-04-15",
    }
    create_resp = client.post("/api/v1/contracts/contracts", json=payload, headers=user1001_headers)
    contract_id = create_resp.json()["data"]["contract_id"]

    patch_resp = client.patch(
        f"/api/v1/contracts/contracts/{contract_id}/status",
        json={"status": "cancelled"},
        headers=user1001_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["data"]["status"] == "cancelled"


def test_contract_cross_org_forbidden(client, user1001_headers, user1002_headers):
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "contract_type": "MEDIUM_LONG",
        "volume_mwh": 1000.0,
        "price": 430.0,
        "start_date": "2026-04-01",
        "end_date": "2026-04-30",
    }
    create_resp = client.post("/api/v1/contracts/contracts", json=payload, headers=user1001_headers)
    contract_id = create_resp.json()["data"]["contract_id"]

    forbidden_resp = client.get(
        f"/api/v1/contracts/contracts/{contract_id}",
        headers=user1002_headers,
    )
    assert forbidden_resp.status_code == 404


def test_contract_not_found(client, user1001_headers):
    resp = client.get("/api/v1/contracts/contracts/CTR-UNKNOWN", headers=user1001_headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "CONTRACT_NOT_FOUND"


def test_contract_invalid_date_range(client, user1001_headers):
    """结束日期早于开始日期应返回 422 验证错误。"""
    payload = {
        "org_id": 1001,
        "province_code": "GD",
        "contract_type": "SPOT_DA",
        "volume_mwh": 100.0,
        "price": 380.0,
        "start_date": "2026-04-30",
        "end_date": "2026-04-01",
    }
    resp = client.post("/api/v1/contracts/contracts", json=payload, headers=user1001_headers)
    assert resp.status_code == 422
    body = resp.json()
    # Pydantic 验证错误可能返回 VALIDATION_ERROR 或在 data 中包含错误详情
    assert body["success"] is False


# ── 风险计算改进 ──────────────────────────────────────────

def test_risk_query_no_history(client, user1001_headers):
    """无历史申报时使用中性偏差率 0.25。"""
    # 使用未来日期确保无历史数据
    resp = client.get(
        "/api/v1/risk/deviation?trade_date=2030-01-01&org_id=1001&province_code=GD",
        headers=user1001_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["deviation_ratio"] == 0.25
    assert body["data"]["deviation_risk_level"] in {"low", "medium", "high"}


def test_risk_query_with_history(client, user1001_headers):
    """有历史申报时偏差率基于真实数据计算。"""
    # 先提交几条申报
    for i in range(3):
        client.post(
            "/api/v1/trades/declarations",
            json={
                "province_code": "GD",
                "trade_date": "2026-04-15",
                "market_type": "SPOT_DA",
                "timeslots": [{"slot": "09:00-09:15", "volume_mwh": 10.0, "price": 420}],
                "idempotency_key": f"risk-test-{i}",
            },
            headers=user1001_headers,
        )

    # 查询次日风险（历史窗口包含上述申报）
    resp = client.get(
        "/api/v1/risk/deviation?trade_date=2026-04-16&org_id=1001&province_code=GD",
        headers=user1001_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    # 偏差率不再是虚假公式的值，应在 [0, 1] 范围
    ratio = body["data"]["deviation_ratio"]
    assert 0.0 <= ratio <= 1.0


# ── 结算汇总报告 ──────────────────────────────────────────

def test_settlement_summary(client, user1001_headers):
    # 先创建申报
    client.post(
        "/api/v1/trades/declarations",
        json={
            "province_code": "GD",
            "trade_date": "2026-04-02",
            "market_type": "SPOT_DA",
            "timeslots": [{"slot": "09:00-09:15", "volume_mwh": 25.0, "price": 430}],
            "idempotency_key": "summary-test-001",
        },
        headers=user1001_headers,
    )

    # 创建结算任务
    create_resp = client.post(
        "/api/v1/settlement/reconcile/tasks",
        json={
            "org_id": 1001,
            "province_code": "GD",
            "cycle_start": "2026-04-01",
            "cycle_end": "2026-04-07",
        },
        headers=user1001_headers,
    )
    assert create_resp.status_code == 200
    task_id = create_resp.json()["data"]["task_id"]

    # 查询汇总报告
    summary_resp = client.get(
        f"/api/v1/settlement/reconcile/tasks/{task_id}/summary",
        headers=user1001_headers,
    )
    assert summary_resp.status_code == 200
    body = summary_resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["task_id"] == task_id
    assert data["province_code"] == "GD"
    assert "total_declarations" in data
    assert "total_volume_mwh" in data
    assert "avg_price" in data
    assert "daily_summary" in data


def test_settlement_summary_not_found(client, user1001_headers):
    resp = client.get(
        "/api/v1/settlement/reconcile/tasks/REC-UNKNOWN/summary",
        headers=user1001_headers,
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == "RECONCILE_TASK_NOT_FOUND"


# ── 看板统计 ──────────────────────────────────────────────

def test_dashboard_stats(client, user1001_headers):
    resp = client.get("/api/v1/dashboard/stats", headers=user1001_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "declarations" in data
    assert "contracts" in data
    assert "reconcile_tasks" in data
    assert "audit_logs" in data
    assert "market" in data
    assert "declaration_trend_7d" in data
    assert isinstance(data["declarations"]["total"], int)


def test_dashboard_stats_admin(client, admin_headers):
    """管理员看板可跨 org 统计。"""
    resp = client.get("/api/v1/dashboard/stats", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
