from typing import List, Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.system import get_system_manager
from app.repositories.submissions_repo import SubmissionsRepo


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

        Returns:
            List of dynamic Pydantic model instances
        """
        dynamic_model = self.system_manager.get_validation_model()

        submissions = await self.repo.fetch_all(offset=0, limit=None)
        return [dynamic_model.model_validate(sub) for sub in submissions]
