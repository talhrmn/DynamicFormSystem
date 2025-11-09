"""
Exception handlers for the FastAPI application.
"""
from typing import Any, Dict, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import DBAPIError, IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.common.exceptions.exceptions import (
    AppBaseException,
    BadRequestException,
    ConflictException,
    DatabaseException,
)
from app.common.logger import get_logger

logger = get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application."""

    app.add_exception_handler(Exception, handle_generic_exception)

    app.add_exception_handler(AppBaseException, handle_app_exception)

    app.add_exception_handler(StarletteHTTPException, handle_http_exception)

    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(PydanticValidationError, handle_pydantic_validation_error)

    app.add_exception_handler(IntegrityError, handle_integrity_error)
    app.add_exception_handler(DBAPIError, handle_db_error)
    app.add_exception_handler(SQLAlchemyError, handle_db_error)


def create_error_response(
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if error_code is None:
        error_code = status.HTTP_500_INTERNAL_SERVER_ERROR.phrase

    error_response = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }

    if details is not None:
        error_response["error"]["details"] = details

    return error_response


async def handle_app_exception(
        request: Request, exc: AppBaseException
) -> JSONResponse:
    """Handle custom application exceptions."""

    if 500 <= exc.status_code < 600:
        logger.error(
            f"Application error: {exc}",
            extra={
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
            },
            exc_info=True,
        )

    error_response = exc.to_dict()

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    status_code = exc.status_code

    if 500 <= status_code < 600:
        logger.error(
            f"HTTP error: {exc.detail}",
            extra={
                "status_code": status_code,
                "path": request.url.path,
            },
            exc_info=True,
        )

    error_response = create_error_response(
        status_code=status_code,
        message=str(exc.detail),
        error_code=exc.__class__.__name__,
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response,
    )


async def handle_validation_error(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        errors.append(
            {
                "field": field or "body",
                "message": error["msg"],
                "type": error["type"],
            }
        )

    error_response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        details={"errors": errors},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def handle_pydantic_validation_error(
        request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append(
            {
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    error_response = create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        details={"errors": errors},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response,
    )


async def handle_integrity_error(
        request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity errors (e.g., unique constraint violations)."""
    logger.error(
        "Database integrity error",
        extra={
            "detail": str(exc),
            "orig": str(exc.orig) if hasattr(exc, "orig") else None,
            "path": request.url.path,
        },
        exc_info=True,
    )

    error_msg = str(exc.orig) if hasattr(exc, "orig") else "Database integrity error"

    if "unique constraint" in error_msg.lower():
        return await handle_app_exception(
            request,
            ConflictException(
                "A record with these details already exists.",
                details={"error": error_msg},
            ),
        )
    elif "foreign key constraint" in error_msg.lower():
        return await handle_app_exception(
            request,
            BadRequestException(
                "Invalid reference in the request.",
                details={"error": error_msg},
            ),
        )

    return await handle_db_error(request, exc)


async def handle_db_error(
        request: Request, exc: Union[DBAPIError, SQLAlchemyError]
) -> JSONResponse:
    """Handle generic database errors."""
    logger.error(
        "Database error",
        extra={
            "detail": str(exc),
            "orig": str(exc.orig) if hasattr(exc, "orig") else None,
            "path": request.url.path,
        },
        exc_info=True,
    )

    return await handle_app_exception(
        request,
        DatabaseException(
            "An error occurred while accessing the database.",
            details={"error": str(exc)},
        ),
    )


async def handle_generic_exception(
        request: Request, exc: Exception
) -> JSONResponse:
    """Handle all other unhandled exceptions."""
    logger.error(
        "Unhandled exception",
        extra={
            "exception_type": exc.__class__.__name__,
            "detail": str(exc),
            "path": request.url.path,
        },
        exc_info=True,
    )

    error_response = create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred.",
        error_code="INTERNAL_SERVER_ERROR",
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )
