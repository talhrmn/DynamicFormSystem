from typing import Any, Type

from sqlalchemy.sql import ColumnElement

from app.common.exceptions import InvalidFilterException
from app.repositories.utils.operators import OperatorHandler


class FilterExpressionFactory:
    """Build SQLAlchemy filter expressions from type/operator/value."""

    @staticmethod
    def build(
            model: Type,
            field_name: str,
            filter_type: str,
            operator_name: str,
            value: Any
    ) -> ColumnElement:
        """Generate a SQLAlchemy expression for a single filter."""
        # Validate column exists
        field = getattr(model, field_name, None)
        if field is None:
            raise InvalidFilterException(f"Column '{field_name}' does not exist on model {model.__name__}")

        # Get operator function
        operators = OperatorHandler.get_filter_operators().get(filter_type)
        if not operators:
            raise InvalidFilterException(f"Unsupported filter type: {filter_type}")

        op_func = operators.get(operator_name)
        if not op_func:
            raise InvalidFilterException(f"Unsupported operator '{operator_name}' for type '{filter_type}'")

        return op_func(field, value)
