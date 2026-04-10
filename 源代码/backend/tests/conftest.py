import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB_PATH = Path(__file__).resolve().parent / "test_power_trading.db"
os.environ["APP_DATABASE_PATH"] = str(TEST_DB_PATH)
os.environ["APP_AUTH_ENABLED"] = "true"
os.environ["APP_AUTH_TOKENS"] = (
    "admin-token:0:admin,user1001-token:1001:trader,user1002-token:1002:trader"
)

from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink(missing_ok=True)
        except PermissionError:
            pass
    yield
    # On Windows the SQLite file may still be held briefly; ignore the error.
    try:
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def user1001_headers():
    return {"Authorization": "Bearer user1001-token"}


@pytest.fixture()
def user1002_headers():
    return {"Authorization": "Bearer user1002-token"}


@pytest.fixture()
def admin_headers():
    return {"Authorization": "Bearer admin-token"}
