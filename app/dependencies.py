from fastapi import Depends
from pydantic import BaseModel
from starlette.requests import Request

from app.core.system import get_system_manager, SystemManager
from app.database.database import get_db_session
from app.services.form_service import FormService
from app.services.submissions_service import SubmissionsService


async def get_submissions_service(
        db_session=Depends(get_db_session),
        system_manager=Depends(get_system_manager)
) -> SubmissionsService:
    return SubmissionsService(system_manager.get_table_model(), db_session)


async def get_form_service(
        db_session=Depends(get_db_session),
        system_manager=Depends(get_system_manager)
) -> FormService:
    return FormService(system_manager.get_table_model(), db_session)


async def get_validated_form_data(
        request: Request,
        system_manager: SystemManager = Depends(get_system_manager),
) -> BaseModel:
    """
    FastAPI dependency to parse & validate form data dynamically.
    Returns a validated Pydantic model instance.
    """
    form_body = await request.form()
    payload = dict(form_body)
    validation_model = system_manager.get_validation_model()
    validated_model = validation_model.model_validate(payload)
    return validated_model
