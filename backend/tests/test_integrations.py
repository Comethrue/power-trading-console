from unittest.mock import patch

from app.core.config import settings


def test_integrations_status(client, user1001_headers):
    r = client.get("/api/v1/integrations/status", headers=user1001_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "trading_center" in body["data"]
    assert "metering" in body["data"]
    assert body["data"]["trading_center"]["configured"] is False


def test_trading_center_not_configured(client, user1001_headers):
    r = client.get(
        "/api/v1/integrations/trading-center/clearing-snapshot",
        headers=user1001_headers,
    )
    assert r.status_code == 503
    assert r.json()["code"] == "INTEGRATION_NOT_CONFIGURED"


def test_metering_not_configured(client, user1001_headers):
    r = client.get(
        "/api/v1/integrations/metering/readings?meter_point_id=M1",
        headers=user1001_headers,
    )
    assert r.status_code == 503
    assert r.json()["code"] == "INTEGRATION_NOT_CONFIGURED"


def test_trading_center_upstream_ok(client, user1001_headers, monkeypatch):
    monkeypatch.setattr(settings, "trading_center_base_url", "http://tc.test")

    def fake_fetch(*_a, **_k):
        return {"deals": [], "ok": True}

    with patch(
        "app.api.endpoints.integrations.tc_client.fetch_clearing_snapshot",
        fake_fetch,
    ):
        r = client.get(
            "/api/v1/integrations/trading-center/clearing-snapshot",
            headers=user1001_headers,
        )
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["source"] == "trading_center"
    assert body["data"]["payload"]["ok"] is True


def test_sso_config_public(client):
    r = client.get("/api/v1/auth/sso/config")
    assert r.status_code == 200
    data = r.json()["data"]
    assert "oidc_enabled" in data
    assert data["oidc_enabled"] is False
