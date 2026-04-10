from fastapi import APIRouter

from app.api.endpoints import (
    audit,
    auth,
    contracts,
    dashboard,
    health,
    integrations,
    market,
    risk,
    rules,
    settlement,
    trades,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(settlement.router, prefix="/settlement", tags=["settlement"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
