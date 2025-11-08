from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepo:
    """Base repository providing transactional context for derived repositories."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def transaction(self):
        """Context manager for transactional operations."""
        async with self.session.begin():
            yield
