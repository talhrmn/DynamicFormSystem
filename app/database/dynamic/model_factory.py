"""
Factory for dynamic SQLAlchemy models generated from form schemas.
"""

from typing import Dict, Type
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, UUID, func

from app.database.base import Base
from .type_mapping import SQLALCHEMY_TYPE_MAPPING
from ...common.schemas import FormSchema

_model_cache: Dict[str, Type] = {}


def create_dynamic_model(form_schema: FormSchema, table_name: str) -> Type:
    """
    Create (or return cached) SQLAlchemy model based on a FormSchema.
    """

    if table_name in _model_cache:
        return _model_cache[table_name]

    # If table exists, reflect existing table
    if table_name in Base.metadata.tables:
        existing = Base.metadata.tables[table_name]
        model = type(table_name.capitalize(), (Base,), {
            "__tablename__": table_name,
            "__table__": existing,
        })
        _model_cache[table_name] = model
        return model

    columns = {
        "__tablename__": table_name,
        "id": Column(UUID(as_uuid=True), primary_key=True, default=uuid4),
        "created_at": Column(DateTime(timezone=True), server_default=func.now()),
    }

    # Add fields from schema
    for field_name, field_schema in form_schema.fields.items():
        sql_type = SQLALCHEMY_TYPE_MAPPING.get(field_schema.type, String)
        kwargs = {"nullable": not field_schema.required}

        if sql_type is String and getattr(field_schema, "max_length", None):
            sql_type = String(field_schema.max_length)

        columns[field_name] = Column(sql_type, **kwargs)

    model = type(table_name.capitalize(), (Base,), columns)
    _model_cache[table_name] = model
    return model


def get_cached_model(table_name: str) -> Type | None:
    """Return cached model by table name."""
    return _model_cache.get(table_name)


def clear_model_cache() -> None:
    """Clear model cache (useful in testing)."""
    _model_cache.clear()
