"""
Factory for generating dynamic Pydantic models from FormSchema.
"""

import hashlib
import json
from datetime import date
from typing import Type, Any, Tuple, Dict, Literal

from pydantic import BaseModel, Field, EmailStr, create_model, ConfigDict

from app.common.enums import SupportedFieldTypes
from app.common.exceptions import InvalidSchemaException
from app.common.schemas import FieldSchema, FormSchema

_dynamic_model_cache: Dict[str, Type[BaseModel]] = {}

"""
Field creator functions.
"""


def _create_string_field(field_name: str, field_schema: FieldSchema) -> Tuple[Type, Any]:
    constraints = {}
    if field_schema.min_length is not None:
        constraints["min_length"] = field_schema.min_length
    if field_schema.max_length is not None:
        constraints["max_length"] = field_schema.max_length
    if field_schema.pattern is not None:
        constraints["pattern"] = field_schema.pattern
    default = ... if field_schema.required else None
    return str, Field(default=default, description=f"Field: {field_name}", **constraints)


def _create_email_field(field_name: str, field_schema: FieldSchema) -> Tuple[Type, Any]:
    default = ... if field_schema.required else None
    return EmailStr, Field(default=default, description=f"Email field: {field_name}")


def _create_password_field(field_name: str, field_schema: FieldSchema) -> Tuple[Type, Any]:
    constraints = {}
    if field_schema.min_length is not None:
        constraints["min_length"] = field_schema.min_length
    if field_schema.max_length is not None:
        constraints["max_length"] = field_schema.max_length
    default = ... if field_schema.required else None
    return str, Field(default=default, description=f"Password field: {field_name}", **constraints)


def _create_date_field(field_name: str, field_schema: FieldSchema) -> Tuple[Type, Any]:
    default = ... if field_schema.required else None
    return date, Field(default=default, description=f"Date field: {field_name}")


def _create_number_field(field_name: str, field_schema: FieldSchema) -> Tuple[Type, Any]:
    constraints = {}
    if field_schema.min is not None:
        constraints["ge"] = field_schema.min
    if field_schema.max is not None:
        constraints["le"] = field_schema.max
    default = ... if field_schema.required else None
    return float, Field(default=default, description=f"Number field: {field_name}", **constraints)


def _create_dropdown_field(field_name: str, field_schema: FieldSchema) -> Tuple[Type, Any]:
    if not field_schema.options:
        raise InvalidSchemaException(f"Dropdown field '{field_name}' must have options.")
    if len(field_schema.options) != len(set(field_schema.options)):
        raise InvalidSchemaException(f"Dropdown field '{field_name}' contains duplicate options.")

    default = ... if field_schema.required else None
    literal_type = Literal[tuple(field_schema.options)]
    return literal_type, Field(
        default=default,
        description=f"Dropdown field: {field_name}. Valid options: {', '.join(field_schema.options)}"
    )


"""
Mapping field types to creator functions
"""
_FIELD_CREATORS = {
    SupportedFieldTypes.TEXT: _create_string_field,
    SupportedFieldTypes.STRING: _create_string_field,
    SupportedFieldTypes.EMAIL: _create_email_field,
    SupportedFieldTypes.PASSWORD: _create_password_field,
    SupportedFieldTypes.DATE: _create_date_field,
    SupportedFieldTypes.NUMBER: _create_number_field,
    SupportedFieldTypes.DROPDOWN: _create_dropdown_field,
}


def generate_dynamic_pydantic_model(schema: FormSchema, model_name: str = "DynamicFormModel") -> Type[BaseModel]:
    """
    Generate a dynamic Pydantic model from a FormSchema.
    Uses caching to avoid regenerating models for the same schema.

    Args:
        schema: FormSchema instance defining the fields
        model_name: Name of the generated Pydantic model class

    Returns:
        Dynamically generated Pydantic model class

    Raises:
        InvalidSchemaException: If schema contains unsupported field types or invalid dropdown options
    """
    schema_dict = {
        "model_name": model_name,
        "fields": {
            name: {
                "type": f.type,
                "required": f.required,
                "min_length": getattr(f, "min_length", None),
                "max_length": getattr(f, "max_length", None),
                "pattern": getattr(f, "pattern", None),
                "min": getattr(f, "min", None),
                "max": getattr(f, "max", None),
                "options": getattr(f, "options", None),
            }
            for name, f in schema.fields.items()
        },
    }
    schema_json = json.dumps(schema_dict, sort_keys=True)
    cache_key = hashlib.sha256(schema_json.encode()).hexdigest()

    if cache_key in _dynamic_model_cache:
        return _dynamic_model_cache[cache_key]

    field_definitions = {}
    for field_name, field_schema in schema.fields.items():
        creator = _FIELD_CREATORS.get(field_schema.type)
        if not creator:
            raise InvalidSchemaException(f"Unsupported field type: {field_schema.type}")
        field_definitions[field_name] = creator(field_name, field_schema)

    dynamic_model = create_model(
        model_name,
        **field_definitions,
        __config__=ConfigDict(use_enum_values=True, from_attributes=True)
    )

    _dynamic_model_cache[cache_key] = dynamic_model
    return dynamic_model


def clear_dynamic_model_cache() -> None:
    """Clear the dynamic Pydantic model cache."""
    _dynamic_model_cache.clear()
