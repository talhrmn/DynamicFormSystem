from typing import Any, List, Optional

from sqlalchemy import select, func, ClauseElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import InvalidSortColumnException
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

    async def fetch_all(
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
