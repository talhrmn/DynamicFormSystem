from typing import List, Type, Iterable

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.system import get_system_manager
from app.jinja.form_filters import parse_filters_from_query_params, get_column_filter_options, col_to_type_mapping
from app.repositories.submissions_repo import SubmissionsRepo
from app.schemas.dashboard.analytics import AnalyticsResponse
from app.schemas.data.submissions import DuplicateGroup, SubmissionsFormResponse
from app.schemas.data.submissions import FieldStats


class SubmissionsService:
    """
    Service layer for managing submissions.
    """

    def __init__(self, table_model: Type, session: AsyncSession):
        self.system_manager = get_system_manager()
        self.repo = SubmissionsRepo(table_model, session)

    async def get_submissions_data(self) -> List[BaseModel]:
        """
        Fetch all submissions without pagination, converted to Pydantic models.
        """
        dynamic_model = self.system_manager.get_validation_model()
        submissions = await self.repo.fetch_submissions(offset=0, limit=None)
        return [dynamic_model.model_validate(sub) for sub in submissions]

    async def get_submissions(
            self,
            query_params: Iterable,
            page: int = 1,
            page_size: int = 10,
            sort_by: str = "created_at",
            sort_desc: bool = True
    ) -> SubmissionsFormResponse:
        """
        Fetch submissions with pagination, sorting, filtering, and UI metadata.
        """
        expressions, ui_conditions = parse_filters_from_query_params(
            query_params,
            self.repo.table_model
        )

        offset = (page - 1) * page_size

        submissions = await self.repo.fetch_submissions(
            offset=offset,
            limit=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc,
            filters=expressions
        )

        total_count = await self.repo.count_filtered_total(filters=expressions)

        submissions_dicts = [
            {c.name: getattr(sub, c.name) for c in sub.__table__.columns} for sub in submissions
        ]

        total_pages = (total_count + page_size - 1) // page_size
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)
        pages = list(range(start_page, end_page + 1))

        columns = self.repo.table_model.__table__.columns.values()
        filter_options = get_column_filter_options(columns)

        return SubmissionsFormResponse(
            submissions=submissions_dicts,
            page=page,
            page_size=page_size,
            pages=pages,
            total=total_count,
            total_pages=total_pages,
            columns=[
                {"name": col.name, "type": col_to_type_mapping(col)}
                for col in self.repo.table_model.__table__.columns
            ],
            filters_applied=ui_conditions,
            sort_by=sort_by,
            sort_desc=sort_desc,
            filter_options=filter_options,
        )

    async def get_duplicates(
            self, key_fields: list[str] = None
    ) -> List[DuplicateGroup]:
        """
        Detect duplicates based on specified key fields.
        """
        if not key_fields:
            key_fields = [col.name for col in self.repo.table_model.__table__.columns if
                          col.name not in ["id", "created_at"]]

        duplicate_rows = await self.repo.get_duplicates(key_fields)

        duplicates = [
            DuplicateGroup(fields={f: getattr(r, f) for f in key_fields}, count=r.cnt)
            for r in duplicate_rows
        ]

        return duplicates

    async def get_field_stats(self) -> List[FieldStats]:
        raw_stats = await self.repo.get_all_field_stats()

        field_stats = [
            FieldStats(
                name=name,
                type=col_to_type_mapping(col),
                non_null_count=vals["non_null"],
                unique_count=vals["unique"]
            )
            for name, vals in raw_stats.items()
            for col in self.repo.table_model.__table__.columns
            if col.name == name
        ]

        return field_stats

    async def get_analytics(self) -> AnalyticsResponse:
        total = await self.repo.count_all()

        duplicates = await self.get_duplicates()

        field_stats = await self.get_field_stats()

        return AnalyticsResponse(
            total_submissions=total,
            duplicates=[d.model_dump() for d in duplicates],
            field_stats=field_stats
        )
