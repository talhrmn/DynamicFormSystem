from sqlalchemy.ext.asyncio import AsyncEngine

from app.database.base import Base


async def create_table_if_not_exists(model_class, engine: AsyncEngine):
    """
    Create table if missing (safely ignores existing tables).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
