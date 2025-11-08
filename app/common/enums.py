from enum import Enum


class SupportedFieldTypes(str, Enum):
    """Supported field types"""
    TEXT = "text"
    STRING = "string"
    EMAIL = "email"
    PASSWORD = "password"
    DATE = "date"
    NUMBER = "number"
    DROPDOWN = "dropdown"


class SupportedColumnTypes(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    UUID = "uuid"


class FilterOperators(str, Enum):
    EQ = "eq"
    CONTAINS = "contains"
    STARTSWITH = "startswith"
    ENDSWITH = "endswith"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    FROM = "from"
    TO = "to"
