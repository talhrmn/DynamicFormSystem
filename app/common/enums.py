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
