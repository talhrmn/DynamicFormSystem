"""
Custom application exceptions.
"""
from typing import Any, Dict, Optional


class AppBaseException(Exception):
    """
    Base class for all custom exceptions.

    Attributes:
        default_message: Default error message for the exception
        status_code: HTTP status code for the error response
        details: Optional additional error details
    """
    default_message: str = "An unexpected application error occurred."
    status_code: int = 500
    details: Optional[Dict[str, Any]] = None

    def __init__(
            self,
            message: Optional[str] = None,
            status_code: Optional[int] = None,
            details: Optional[Dict[str, Any]] = None
    ):
        self.message = message or self.default_message
        self.status_code = status_code or self.status_code
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for JSON responses."""
        result = {
            "error": {
                "code": self.__class__.__name__,
                "message": self.message,
                "status_code": self.status_code
            }
        }
        if self.details:
            result["error"]["details"] = self.details
        return result


class SchemaNotLoadedException(AppBaseException):
    """Raised when no schema is currently available."""
    default_message = "Schema has not been loaded yet."
    status_code = 503


class InvalidSchemaException(AppBaseException):
    """Raised when a schema is invalid, corrupted, or cannot be parsed."""
    default_message = "The provided schema is invalid."
    status_code = 400


class SchemaMissingException(AppBaseException):
    """Raised when a schema is missing."""
    default_message = "The provided path to the schema is incorrect or missing."
    status_code = 404


class TableModelException(AppBaseException):
    """Raised when there's an issue with a table model."""
    default_message = "Table model is missing or invalid."
    status_code = 500


class ValidationException(AppBaseException):
    """Base class for validation errors."""
    default_message = "Validation failed for the provided data."
    status_code = 422


class RequiredFieldException(ValidationException):
    """Raised when a required field is missing."""
    default_message = "Required field is missing."
    status_code = 400

    def __init__(self, field: str, **kwargs):
        message = f"Required field '{field}' is missing."
        super().__init__(message=message, details={"field": field}, **kwargs)


class InvalidFieldTypeException(ValidationException):
    """Raised when a field has an invalid type."""
    default_message = "Invalid field type."
    status_code = 400

    def __init__(self, field: str, expected_type: str, actual_type: str, **kwargs):
        message = f"Field '{field}' must be of type {expected_type}, got {actual_type}"
        details = {
            "field": field,
            "expected_type": expected_type,
            "actual_type": actual_type
        }
        super().__init__(message=message, details=details, **kwargs)


class DatabaseException(AppBaseException):
    """Base class for database-related errors."""
    default_message = "A database error occurred."
    status_code = 500


class RecordNotFoundException(DatabaseException):
    """Raised when a requested record is not found."""
    default_message = "The requested record was not found."
    status_code = 404

    def __init__(self, model: str, **kwargs):
        message = f"{model} not found."
        super().__init__(message=message, details={"model": model}, **kwargs)


class DuplicateRecordException(DatabaseException):
    """Raised when a duplicate record is detected."""
    default_message = "A record with these details already exists."
    status_code = 409


class DatabaseConnectionException(DatabaseException):
    """Raised when there's an issue connecting to the database."""
    default_message = "Could not connect to the database."
    status_code = 503


class BusinessRuleException(AppBaseException):
    """Base class for business rule violations."""
    default_message = "Business rule violation."
    status_code = 400


class InvalidOperationException(BusinessRuleException):
    """Raised when an invalid operation is attempted."""
    default_message = "The requested operation is not allowed."
    status_code = 403


class BadRequestException(AppBaseException):
    """Raised for malformed or invalid client requests."""
    default_message = "The request could not be processed."
    status_code = 400


class UnauthorizedException(AppBaseException):
    """Raised when authentication is required but not provided or invalid."""
    default_message = "Authentication is required to access this resource."
    status_code = 401


class ForbiddenException(AppBaseException):
    """Raised when the user doesn't have permission to access a resource."""
    default_message = "You don't have permission to access this resource."
    status_code = 403


class NotFoundException(AppBaseException):
    """Raised when a requested resource is not found."""
    default_message = "The requested resource was not found."
    status_code = 404


class MethodNotAllowedException(AppBaseException):
    """Raised when an unsupported HTTP method is used."""
    default_message = "The requested method is not allowed for this resource."
    status_code = 405


class ConflictException(AppBaseException):
    """Raised when there's a conflict with the current state of the resource."""
    default_message = "The request conflicts with the current state of the resource."
    status_code = 409


class UnprocessableEntityException(AppBaseException):
    """Raised when the request is well-formed but contains semantic errors."""
    default_message = "The request was well-formed but contains semantic errors."
    status_code = 422


class RateLimitExceededException(AppBaseException):
    """Raised when the rate limit has been exceeded."""
    default_message = "Rate limit exceeded. Please try again later."
    status_code = 429


class InternalServerError(AppBaseException):
    """Raised when an unexpected server error occurs."""
    default_message = "An unexpected error occurred on the server."
    status_code = 500


class ServiceUnavailableException(AppBaseException):
    """Raised when a required service is unavailable."""
    default_message = "The service is temporarily unavailable. Please try again later."
    status_code = 503


class ModelGenerationException(AppBaseException):
    """Raised when dynamic model generation fails."""
    default_message = "Failed to generate dynamic model."
    status_code = 500


class InvalidFilterException(AppBaseException):
    """Raised when attempting to filter by a column that doesn't exist."""
    default_message = "Invalid filter request."
    status_code = 400


class InvalidSortColumnException(AppBaseException):
    """Raised when attempting to sort by a column that doesn't exist."""
    default_message = "Invalid sort column specified."
    status_code = 40
