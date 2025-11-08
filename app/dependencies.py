from fastapi import Depends

from app.core.system import get_system_manager
from app.database.database import get_db_session
from app.services.submissions_service import SubmissionsService


async def get_submissions_service(
        db_session=Depends(get_db_session),
        system_manager=Depends(get_system_manager)
) -> SubmissionsService:
    return SubmissionsService(system_manager.get_table_model(), db_session)
