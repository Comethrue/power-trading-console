from datetime import date
from pathlib import Path

import yaml

from app.core.errors import AppException, ErrorCode
from app.schemas.rules import ProvinceRule
from app.schemas.settlement import ReconcileTaskRequest
from app.schemas.trades import TradeDeclarationRequest

RULES_BASE_DIR = Path(__file__).resolve().parents[2] / "rules" / "provinces"


def _province_dir(province_code: str) -> Path:
    return RULES_BASE_DIR / province_code.upper()


def _load_rule_file(path: Path) -> ProvinceRule:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ProvinceRule.model_validate(raw)


def _list_rule_files(province_code: str) -> list[Path]:
    pdir = _province_dir(province_code)
    if not pdir.exists():
        return []
    return sorted(p for p in pdir.glob("*.yaml") if p.is_file())


def list_rule_versions(province_code: str) -> list[str]:
    versions = []
    for file in _list_rule_files(province_code):
        versions.append(file.stem)
    return sorted(versions, reverse=True)


def _select_rule_by_date(rules: list[ProvinceRule], trade_date: date) -> ProvinceRule | None:
    for rule in sorted(rules, key=lambda x: x.version, reverse=True):
        if rule.effective_start <= trade_date and (
            rule.effective_end is None or trade_date <= rule.effective_end
        ):
            return rule
    return None


def get_rule(
    province_code: str,
    version: str | None = None,
    trade_date: date | None = None,
) -> ProvinceRule:
    files = _list_rule_files(province_code)
    if not files:
        raise AppException(
            code=ErrorCode.RULE_NOT_FOUND,
            message=f"no rule files for province {province_code}",
            status_code=404,
        )

    rules = [_load_rule_file(file) for file in files]

    if version:
        for rule in rules:
            if rule.version == version:
                return rule
        raise AppException(
            code=ErrorCode.RULE_NOT_FOUND,
            message=f"rule version {version} not found for province {province_code}",
            status_code=404,
        )

    if trade_date is not None:
        selected = _select_rule_by_date(rules, trade_date)
        if selected:
            return selected
        raise AppException(
            code=ErrorCode.RULE_NOT_FOUND,
            message=f"no rule matched for date {trade_date.isoformat()} in province {province_code}",
            status_code=404,
        )

    return sorted(rules, key=lambda x: x.version, reverse=True)[0]


def resolve_trade_rule(payload: TradeDeclarationRequest) -> ProvinceRule:
    return get_rule(
        province_code=payload.province_code,
        version=payload.rule_version,
        trade_date=payload.trade_date,
    )


def validate_trade_with_rule(payload: TradeDeclarationRequest, rule: ProvinceRule) -> None:
    if len(payload.timeslots) > rule.trade.timeslot_max_count:
        raise AppException(
            code=ErrorCode.RULE_VALIDATION_ERROR,
            message=(
                f"timeslot count {len(payload.timeslots)} exceeds limit "
                f"{rule.trade.timeslot_max_count}"
            ),
            status_code=400,
        )

    for idx, slot in enumerate(payload.timeslots, start=1):
        if not (rule.trade.price_min <= slot.price <= rule.trade.price_max):
            raise AppException(
                code=ErrorCode.RULE_VALIDATION_ERROR,
                message=(
                    f"timeslot #{idx} price {slot.price} out of range "
                    f"[{rule.trade.price_min}, {rule.trade.price_max}]"
                ),
                status_code=400,
            )
        if not (rule.trade.volume_min <= slot.volume_mwh <= rule.trade.volume_max):
            raise AppException(
                code=ErrorCode.RULE_VALIDATION_ERROR,
                message=(
                    f"timeslot #{idx} volume {slot.volume_mwh} out of range "
                    f"[{rule.trade.volume_min}, {rule.trade.volume_max}]"
                ),
                status_code=400,
            )


def resolve_settlement_rule(payload: ReconcileTaskRequest) -> ProvinceRule:
    return get_rule(
        province_code=payload.province_code,
        version=payload.rule_version,
        trade_date=payload.cycle_start,
    )


def validate_settlement_with_rule(payload: ReconcileTaskRequest, rule: ProvinceRule) -> None:
    cycle_days = (payload.cycle_end - payload.cycle_start).days + 1
    if cycle_days > rule.settlement.max_cycle_days:
        raise AppException(
            code=ErrorCode.RULE_VALIDATION_ERROR,
            message=(
                f"settlement cycle days {cycle_days} exceeds max "
                f"{rule.settlement.max_cycle_days}"
            ),
            status_code=400,
        )
