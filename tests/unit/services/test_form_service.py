"""Unit tests for the FormService class."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import FormSchema
from app.jinja.form_renderer import FormContext
from app.services.form_service import FormService


class TestFormService:
    """Test suite for FormService class."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def form_service(self, mock_session):
        """Create a FormService instance with a mock session."""
        mock_table = MagicMock()
        return FormService(table_model=mock_table, session=mock_session)

    @pytest.fixture
    def test_form_schema(self):
        """Return a test form schema."""
        return {
            "name": {"type": "string", "required": True, "minLength": 3},
            "email": {"type": "email", "required": True},
            "age": {"type": "number", "required": True, "min": 18},
        }

    @pytest.mark.asyncio
    async def test_get_form_context(self, form_service, test_form_schema):
        """Test getting form context with valid schema."""

        form_schema = FormSchema(fields=test_form_schema)

        context = await form_service.get_form_context(
            form_schema=form_schema,
            values={"name": "Test User", "email": "test@example.com"},
            errors={"age": "This field is required"},
            form_title="Test Form",
            form_action="/submit"
        )

        assert isinstance(context, FormContext)
        assert context.form_title == "Test Form"
        assert context.form_action == "/submit"
        assert len(context.fields) == 3

        name_field = next(f for f in context.fields if f.name == "name")
        assert name_field.value == "Test User"
        assert name_field.required is True

        age_field = next(f for f in context.fields if f.name == "age")
        assert age_field.error == "This field is required"

    @pytest.mark.asyncio
    async def test_get_form_context_with_success_message(self, form_service, test_form_schema):
        """Test getting form context with success message."""

        form_schema = FormSchema(fields=test_form_schema)
        success_message = "Form submitted successfully!"

        context = await form_service.get_form_context(
            form_schema=form_schema,
            success_message=success_message
        )

        assert context.success_message == success_message

    @pytest.mark.asyncio
    async def test_get_form_context_with_empty_schema(self, form_service):
        """Test getting form context with an empty schema."""

        form_schema = FormSchema(fields={})

        context = await form_service.get_form_context(form_schema=form_schema)

        assert len(context.fields) == 0

    @pytest.mark.asyncio
    async def test_get_form_context_with_default_values(self, form_service, test_form_schema):
        """Test getting form context with default values."""

        form_schema = FormSchema(fields=test_form_schema)

        context = await form_service.get_form_context(form_schema=form_schema)

        assert context is not None
