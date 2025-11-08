from enum import Enum
from functools import lru_cache
import operator
from sqlalchemy.sql import ColumnElement
from typing import Any, Dict

from app.common.enums import FilterOperators, SupportedColumnTypes


class OperatorHandler:
    """Class holding mappings from filter operators to SQLAlchemy expressions."""

    STRING_OPERATORS = {
        FilterOperators.EQ.value: operator.eq,
        FilterOperators.CONTAINS.value: lambda col, val: col.ilike(f"%{val}%"),
        FilterOperators.STARTSWITH.value: lambda col, val: col.ilike(f"{val}%"),
        FilterOperators.ENDSWITH.value: lambda col, val: col.ilike(f"%{val}"),
    }

    NUMBER_OPERATORS = {
        FilterOperators.EQ.value: operator.eq,
        FilterOperators.LT.value: operator.lt,
        FilterOperators.LTE.value: operator.le,
        FilterOperators.GT.value: operator.gt,
        FilterOperators.GTE.value: operator.ge,
    }

    BOOLEAN_OPERATORS = {
        FilterOperators.EQ.value: lambda col, val: col.is_(val),
    }

    DATE_OPERATORS = {
        FilterOperators.EQ.value: operator.eq,
        FilterOperators.FROM.value: lambda col, val: col >= val,
        FilterOperators.TO.value: lambda col, val: col <= val,
        FilterOperators.LT.value: operator.lt,
        FilterOperators.LTE.value: operator.le,
        FilterOperators.GT.value: operator.gt,
        FilterOperators.GTE.value: operator.ge,
    }

    UUID_OPERATORS = {
        FilterOperators.EQ.value: operator.eq,
    }

    FILTER_OPERATORS: Dict[str, Dict[str, Any]] = {
        SupportedColumnTypes.STRING.value: STRING_OPERATORS,
        SupportedColumnTypes.NUMBER.value: NUMBER_OPERATORS,
        SupportedColumnTypes.BOOLEAN.value: BOOLEAN_OPERATORS,
        SupportedColumnTypes.DATE.value: DATE_OPERATORS,
        SupportedColumnTypes.UUID.value: UUID_OPERATORS,
    }

    @classmethod
    @lru_cache
    def get_filter_operators(cls) -> Dict[str, Dict[str, Any]]:
        """Return cached filter operator mappings."""
        return cls.FILTER_OPERATORS
