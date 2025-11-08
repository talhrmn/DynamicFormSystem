import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple, Any, Iterable

from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, UUID
from sqlalchemy.sql import ColumnElement

from app.common.enums import SupportedColumnTypes
from app.repositories.utils.operators import OperatorHandler

filter_operators = OperatorHandler.get_filter_operators()


@dataclass
class FilterCondition:
    field: str
    operator: str
    raw_value: str
    value: Any


def _infer_logical_type_from_column(col) -> str:
    """Infer logical filter type from a SQLAlchemy column object."""
    sa_type = col.type
    if isinstance(sa_type, UUID):
        return SupportedColumnTypes.UUID.value
    if isinstance(sa_type, (String, Text)):
        return SupportedColumnTypes.STRING.value
    if isinstance(sa_type, (Integer, Float)):
        return SupportedColumnTypes.NUMBER.value
    if isinstance(sa_type, Boolean):
        return SupportedColumnTypes.BOOLEAN.value
    if isinstance(sa_type, (Date, DateTime)):
        return SupportedColumnTypes.DATE.value
    return SupportedColumnTypes.STRING.value


def _parse_value(logical_type: str, raw: str):
    """Parse raw string into Python value according to logical type."""
    raw = (raw or "").strip()
    if raw == "":
        return None

    if logical_type == SupportedColumnTypes.UUID.value:
        try:
            return uuid.UUID(raw)
        except ValueError:
            return raw

    if logical_type == SupportedColumnTypes.NUMBER.value:
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw

    if logical_type == SupportedColumnTypes.BOOLEAN.value:
        lowered = raw.lower()
        if lowered in ("true", "1", "yes", "y"):
            return True
        if lowered in ("false", "0", "no", "n"):
            return False
        return raw

    if logical_type == SupportedColumnTypes.DATE.value:
        try:
            return datetime.fromisoformat(raw)
        except Exception:
            return raw

    return raw  # string fallback


def parse_filters_from_query_params(
        query_params: Iterable[Tuple[str, str]],
        table,
) -> Tuple[List[ColumnElement], Dict[str, List[FilterCondition]]]:
    """
    Parses query params into SQLAlchemy expressions + UI-ready FilterCondition map.

    query_params: iterable of (key, value) pairs (e.g. request.query_params.multi_items()).
    table: SQLAlchemy ORM class (dynamic table) with __table__.columns.
    """
    expressions: List[ColumnElement] = []
    ui_conditions: Dict[str, List[FilterCondition]] = {}

    # Group params by field (supporting suffixes e.g. age__op=gte, age__value=30)
    field_map: Dict[str, Dict[str, str]] = {}
    for key, value in query_params:
        if key in ("page", "page_size", "sort_by", "sort_desc"):
            continue
        if "__" in key:
            field, suffix = key.split("__", 1)
        else:
            field, suffix = key, "value"
        field_map.setdefault(field, {})[suffix] = value

    for field, data in field_map.items():
        col_obj = table.__table__.columns.get(field)
        if col_obj is None:
            # unknown column skip
            continue

        logical_type = _infer_logical_type_from_column(col_obj)
        supported_ops = filter_operators.get(logical_type, {})

        # single operator + value (op defaults to 'eq')
        op = data.get("op", "eq")
        raw_value = data.get("value")
        if raw_value and op in supported_ops:
            parsed_value = _parse_value(logical_type, raw_value)
            try:
                expr = supported_ops[op](getattr(table, field), parsed_value)
                expressions.append(expr)
                ui_conditions.setdefault(field, []).append(
                    FilterCondition(field, op, raw_value, parsed_value)
                )
            except Exception:
                # ignore bad parsing or operator application
                continue

        # date-specific range handling using 'from' and 'to' keys
        if logical_type == "date":
            for date_key in ("from", "to"):
                raw_date = data.get(date_key)
                if not raw_date:
                    continue
                if date_key not in supported_ops:
                    continue
                parsed_date = _parse_value(logical_type, raw_date)
                try:
                    expr = supported_ops[date_key](getattr(table, field), parsed_date)
                    expressions.append(expr)
                    ui_conditions.setdefault(field, []).append(
                        FilterCondition(field, date_key, raw_date, parsed_date)
                    )
                except Exception:
                    continue

    return expressions, ui_conditions


def get_column_filter_options(columns):
    """
    Given SQLAlchemy columns (iterable), returns mapping column_name -> supported operator keys.
    Useful for building filter UI.
    """
    options = {}
    for col in columns:
        logical_type = _infer_logical_type_from_column(col)
        ops = list(filter_operators.get(logical_type, {}).keys())
        options[col.name] = ops
    return options
