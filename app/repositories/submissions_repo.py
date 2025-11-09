from typing import Any, List, Optional

from sqlalchemy import select, func, ClauseElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions.exceptions import InvalidSortColumnException
from app.repositories.base_repo import BaseRepo


class SubmissionsRepo(BaseRepo):
    """Repository to handle dynamic form submissions."""

    def __init__(self, table_model: type, session: AsyncSession):
        self.table_model = table_model
        super().__init__(session=session)

    async def insert_submission(self, data: Any) -> Any:
        """Insert a new submission and return the inserted row."""
        db_data = self.table_model(**data.model_dump())
        async with self.transaction():
            self.session.add(db_data)
            await self.session.flush()
        return db_data

    async def fetch_submissions(
            self,
            offset: int = 0,
            limit: Optional[int] = 10,
            sort_by: str = "created_at",
            sort_desc: bool = True,
            filters: Optional[List[ClauseElement]] = None,
    ) -> List[Any]:
        """Fetch rows with optional filters, ordering, and pagination."""
        async with self.transaction():
            query = select(self.table_model)

            # Apply filters
            if filters:
                for expr in filters:
                    query = query.where(expr)

            # Apply sorting
            col = getattr(self.table_model, sort_by, None)
            if col is None:
                raise InvalidSortColumnException(f"Column '{sort_by}' does not exist")
            query = query.order_by(col.desc() if sort_desc else col.asc())

            # Apply pagination
            if offset > 0:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            result = await self.session.execute(query)
            return result.scalars().all()

    async def count_all(self) -> int:
        """Count total number of rows."""
        async with self.transaction():
            query = select(func.count()).select_from(self.table_model)
            result = await self.session.execute(query)
            return int(result.scalar() or 0)

    async def count_filtered_total(self, filters: Optional[List[ClauseElement]] = None) -> int:
        """
        Count rows matching the given filters.
        """
        async with self.transaction():
            query = select(func.count()).select_from(self.table_model)
            if filters:
                for expr in filters:
                    query = query.where(expr)

            result = await self.session.execute(query)
            return int(result.scalar() or 0)

    async def get_duplicates(self, key_fields: list[str]) -> List[Any]:
        """
        Find submissions that are duplicates based on key fields.
        """
        async with self.transaction():
            cols = [getattr(self.table_model, f) for f in key_fields]
            query = (
                select(*cols, func.count().label("cnt"))
                .group_by(*cols)
                .having(func.count() > 1)
            )
            results = await self.session.execute(query)
            return results.all()

    async def get_field_non_null_count(self, column_name: str) -> int:
        """
        Find non-null count by field.
        """
        col = getattr(self.table_model, column_name)
        async with self.transaction():
            query = select(func.count()).where(col.is_not(None))
            result = await self.session.execute(query)
            return int(result.scalar() or 0)

    async def get_field_unique_count(self, column_name: str) -> int:
        """
        Find unique count by field.
        """
        col = getattr(self.table_model, column_name)
        async with self.transaction():
            stmt = select(func.count(func.distinct(col)))
            result = await self.session.execute(stmt)
            return int(result.scalar() or 0)

    async def get_all_field_stats(self) -> dict[str, dict[str, int]]:
        stats = {}
        for col in self.table_model.__table__.columns:
            name = col.name
            non_null = await self.get_field_non_null_count(name)
            unique = await self.get_field_unique_count(name)
            stats[name] = {"non_null": non_null, "unique": unique}
        return stats
