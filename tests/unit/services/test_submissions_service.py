"""Unit tests for the SubmissionsService class."""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

from app.core.system import get_system_manager
from app.schemas.data.submissions import SubmissionsFormResponse, FieldStats
from app.services.submissions_service import SubmissionsService


class TestSubmissionsService:
    """Test suite for SubmissionsService class."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_table_model(self):
        """Create a mock table model with some columns."""

        Base = declarative_base()

        class MockTable(Base):
            __tablename__ = 'test_table'
            __table_args__ = {'extend_existing': True}

            id = Column(Integer, primary_key=True)
            name = Column(String)
            email = Column(String)
            age = Column(Integer)
            gender = Column(String)
            created_at = Column(DateTime, default=datetime.utcnow)

        return MockTable

    @pytest.fixture
    def submissions_service(self, mock_table_model, mock_session, initialized_system):
        """Create a SubmissionsService instance with mocks and initialized system."""

        system_manager = get_system_manager()

        return SubmissionsService(table_model=mock_table_model, session=mock_session)

    @pytest.fixture
    def test_submissions(self):
        """Return a list of test submissions."""
        return [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30, "gender": "male",
             "created_at": "2023-01-01T00:00:00"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25, "gender": "female",
             "created_at": "2023-01-02T00:00:00"},
            {"id": 3, "name": "Alex Johnson", "email": "alex@example.com", "age": 35, "gender": "other",
             "created_at": "2023-01-03T00:00:00"},
        ]

    @pytest.fixture
    def mock_submission_objects(self, mock_table_model):
        """Create mock SQLAlchemy model instances."""

        def create_mock_submission(**kwargs):
            """Create a mock submission object that behaves like a SQLAlchemy model."""
            mock = MagicMock(spec=mock_table_model)
            mock.__table__ = mock_table_model.__table__

            for key, value in kwargs.items():
                setattr(mock, key, value)

            return mock

        return [
            create_mock_submission(id=1, name="John Doe", email="john@example.com",
                                   age=30, gender="male", created_at="2023-01-01T00:00:00"),
            create_mock_submission(id=2, name="Jane Smith", email="jane@example.com",
                                   age=25, gender="female", created_at="2023-01-02T00:00:00"),
            create_mock_submission(id=3, name="Alex Johnson", email="alex@example.com",
                                   age=35, gender="other", created_at="2023-01-03T00:00:00"),
        ]

    @pytest.mark.asyncio
    async def test_get_submissions_data(self, submissions_service, test_submissions):
        """Test fetching all submissions data."""

        submissions_service.system_manager.get_validation_model = MagicMock()
        submissions_service.repo.fetch_submissions = AsyncMock(return_value=test_submissions)

        validation_model = MagicMock()
        validation_model.model_validate.side_effect = lambda x: x
        submissions_service.system_manager.get_validation_model.return_value = validation_model

        result = await submissions_service.get_submissions_data()

        assert len(result) == len(test_submissions)
        submissions_service.repo.fetch_submissions.assert_called_once_with(offset=0, limit=None)
        assert validation_model.model_validate.call_count == len(test_submissions)

    @pytest.mark.asyncio
    async def test_get_submissions_with_pagination(self, submissions_service, mock_submission_objects):
        """Test fetching submissions with pagination."""

        test_data = mock_submission_objects[:2]
        test_count = len(mock_submission_objects)

        submissions_service.repo.fetch_submissions = AsyncMock(return_value=test_data)
        submissions_service.repo.count_filtered_total = AsyncMock(return_value=test_count)

        submissions_service.get_field_stats = AsyncMock(return_value=[
            FieldStats(name="name", type="string", non_null_count=3, unique_count=3),
            FieldStats(name="email", type="string", non_null_count=3, unique_count=3),
        ])

        result = await submissions_service.get_submissions(
            query_params=[],
            page=1,
            page_size=2,
            sort_by="name",
            sort_desc=False
        )

        assert isinstance(result, SubmissionsFormResponse)
        assert result.total == test_count
        assert len(result.submissions) == len(test_data)
        assert result.page == 1
        assert result.pages == [1, 2]
        submissions_service.repo.fetch_submissions.assert_called_once()
        submissions_service.repo.count_filtered_total.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_submissions_with_filters(self, submissions_service, mock_submission_objects):
        """Test fetching submissions with filters."""

        filtered_data = [sub for sub in mock_submission_objects if sub.name == "John Doe"]

        submissions_service.repo.fetch_submissions = AsyncMock(return_value=filtered_data)
        submissions_service.repo.count_filtered_total = AsyncMock(return_value=len(filtered_data))

        submissions_service.get_field_stats = AsyncMock(return_value=[
            FieldStats(name="name", type="string", non_null_count=1, unique_count=1),
        ])

        result = await submissions_service.get_submissions(
            query_params=[("name", "eq:John Doe")],
            page=1,
            page_size=10
        )

        assert result.total == 1
        assert len(result.submissions) == 1
        assert result.submissions[0]["name"] == "John Doe"
        submissions_service.repo.fetch_submissions.assert_called_once()
        submissions_service.repo.count_filtered_total.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_field_stats(self, submissions_service):
        """Test getting field statistics."""

        test_stats = {
            "name": {"non_null": 3, "unique": 3},
            "email": {"non_null": 3, "unique": 3},
            "age": {"non_null": 3, "unique": 3},
            "gender": {"non_null": 3, "unique": 3},
        }

        submissions_service.repo.get_all_field_stats = AsyncMock(return_value=test_stats)

        result = await submissions_service.get_field_stats()

        assert isinstance(result, list)
        assert len(result) == 4

        for stat in result:
            assert isinstance(stat, FieldStats)
            assert hasattr(stat, 'name')
            assert hasattr(stat, 'type')
            assert hasattr(stat, 'non_null_count')
            assert hasattr(stat, 'unique_count')
            assert stat.non_null_count == 3
            assert stat.unique_count == 3

        submissions_service.repo.get_all_field_stats.assert_called_once()

        field_names = {stat.name for stat in result}
        assert "name" in field_names
        assert "email" in field_names
        assert "age" in field_names
        assert "gender" in field_names
