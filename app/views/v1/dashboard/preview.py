from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from starlette import status

from app.common.logger import get_logger
from app.core.system import SystemManager, get_system_manager
from app.jinja.templates import templates
from app.services.form_service import FormService

logger = get_logger()

router = APIRouter(prefix="/preview")


@router.get("/", name="preview_form", response_class=HTMLResponse)
async def preview_form(
        request: Request,
        system_manager: SystemManager = Depends(get_system_manager),
):
    form_schema = system_manager.get_form_schema()
    fields_info = await FormService.get_schema_preview(form_schema)
    return templates.TemplateResponse(
        "preview.html", {
            "request": request,
            **fields_info
        },
        status_code=status.HTTP_200_OK
    )
