# Backend Quick Start

## 1. Install dependencies

```powershell
cd backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For test dependencies:

```powershell
pip install -r requirements-dev.txt
```

## 2. Configure environment

```powershell
Copy-Item .env.example .env
```

## 3. Run service

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. Useful endpoints

- `GET /` root message
- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/whoami`
- `GET /api/v1/rules?province_code=GD&trade_date=2026-04-09`
- `GET /api/v1/rules/versions?province_code=GD`
- `POST /api/v1/trades/declarations`
- `GET /api/v1/trades/declarations/{declaration_id}`
- `GET /api/v1/trades/declarations?page_no=1&page_size=20`
- `GET /api/v1/risk/deviation?trade_date=2026-04-09&org_id=1001&province_code=GD`
- `POST /api/v1/settlement/reconcile/tasks`
- `GET /api/v1/settlement/reconcile/tasks/{task_id}`
- `GET /api/v1/settlement/reconcile/tasks?page_no=1&page_size=20`
- `PATCH /api/v1/settlement/reconcile/tasks/{task_id}/status`
- `GET /api/v1/market/prices?province_code=GD&page_no=1&page_size=20`
- `GET /api/v1/audit/logs?page_no=1&page_size=20`

## 5. Notes

- The current MVP uses SQLite for local persistence.
- DB file path is configured via `APP_DATABASE_PATH` in `.env`.
- Standard response includes `success`, `code`, `message`, `data`, `request_id`.
- Rule files are in `backend/rules/provinces/{PROVINCE}/{VERSION}.yaml`.
- Frontend console is served at `/console`.
- Protected APIs require `Authorization: Bearer <token>`.
- Default tokens:
  - `admin-token` (admin, org_id=0)
  - `user1001-token` (trader, org_id=1001)
  - `user1002-token` (trader, org_id=1002)
- JWT login users:
  - `admin / admin123`
  - `user1001 / pass1001`
  - `user1002 / pass1002`
- Login now returns both `access_token` and `refresh_token`.

## 6. Import sample market prices

```powershell
python scripts/import_market_data.py --db .\power_trading.db --csv .\data\sample_market_prices.csv --source sample
```

## 7. Seed demo data (contracts, declarations, tasks, audit logs)

```powershell
# Insert demo data (idempotent, safe to run multiple times)
python scripts/seed_data.py

# Clear and re-insert
python scripts/seed_data.py --clear
```

> Demo data includes:
> - 7 contracts (GD + ZJ, active + expired)
> - 20 trade declarations (8 days × 2 orgs, each with 96 timeslots)
> - 6 reconcile tasks (completed + running + queued)
> - 18 audit log entries

## 8. Run tests

```powershell
pytest -q
```
