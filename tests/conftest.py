"""
Test configuration and fixtures for the Dynamic Form System.
"""
from typing import AsyncGenerator, Dict, Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.common.schemas import FieldSchema
from app.common.schemas import FormSchema
from app.core.config import get_settings
from app.core.system import get_system_manager
from app.database.base import Base
from app.database.database import get_db_session
from app.main import app as _app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

TEST_FORM_SCHEMA = {
    "name": {"type": "string", "required": True, "minLength": 3},
    "email": {"type": "email", "required": True},
    "age": {"type": "number", "required": True, "min": 18},
    "gender": {
        "type": "dropdown",
        "options": ["male", "female", "other"],
        "required": True
    }
}

settings = get_settings()
settings.DATABASE_URL = TEST_DATABASE_URL

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a clean test database for each test case."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def initialized_system():
    """Initialize the system manager with test schema."""
    system_manager = get_system_manager()

    system_manager._form_schema = None
    system_manager._validation_model = None
    system_manager._table_model = None
    system_manager.schema_loaded = False

    fields = {}
    for field_name, field_def in TEST_FORM_SCHEMA.items():
        fields[field_name] = FieldSchema(**field_def)

    system_manager._form_schema = FormSchema(fields=fields)
    system_manager.schema_loaded = True

    return system_manager


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession, initialized_system) -> TestClient:
    """Create a test client with initialized dependencies."""

    async def _get_test_db():
        try:
            yield db_session
        finally:
            await db_session.rollback()

    system_manager = get_system_manager()

    _app.dependency_overrides[get_db_session] = _get_test_db

    with TestClient(_app) as test_client:
        yield test_client

    _app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_form_schema() -> Dict[str, Any]:
    """Return a test form schema."""
    return {
        "name": {
            "type": "string",
            "required": True,
            "minLength": 3,
            "label": "Full Name"
        },
        "email": {
            "type": "email",
            "required": True,
            "label": "Email Address"
        },
        "age": {
            "type": "number",
            "required": True,
            "min": 18,
            "label": "Your Age"
        },
        "gender": {
            "type": "dropdown",
            "options": ["male", "female", "other", "prefer not to say"],
            "required": True,
            "label": "Gender"
        },
        "interests": {
            "type": "multiselect",
            "options": ["sports", "music", "reading", "traveling"],
            "required": False,
            "label": "Your Interests"
        },
        "bio": {
            "type": "textarea",
            "required": False,
            "maxLength": 500,
            "label": "About You"
        },
        "subscribe": {
            "type": "checkbox",
            "required": False,
            "label": "Subscribe to newsletter"
        }
    }
