"""
Custom application exceptions.
"""


class AppBaseException(Exception):
    """
    Base class for all custom exceptions.
    """
    default_message: str = "An unexpected application error occurred."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


"""
Schema related exceptions
"""

class SchemaNotLoadedException(AppBaseException):
    """
    Raised when no schema is currently available.
    """
    default_message = "Schema has not been loaded yet."


class InvalidSchemaException(AppBaseException):
    """
    Raised when a schema is invalid, corrupted, or cannot be parsed.
    """
    default_message = "The provided schema is invalid."


class SchemaMissingException(AppBaseException):
    """
    Raised when a schema is missing.
    """
    default_message = "The provided path to the schema is incorrect or missing."


class TableModelException(AppBaseException):
    """
    Raised when a table model is missing.
    """
    default_message = "Table model or missing."

"""
App related exceptions
"""

class ModelGenerationException(AppBaseException):
    """
    Raised when dynamic model generation fails.
    """
    default_message = "Failed to generate dynamic model."

class InvalidFilterException(AppBaseException):
    """
    Raised when attempting to filter by a column that doesn't exist.
    """
    default_message = "Invalid filter request."

class InvalidSortColumnException(Exception):
    """Raised when attempting to sort by a column that doesn't exist."""
    default_message = "Invalid sort request."