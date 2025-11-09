from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from starlette import status
from starlette.requests import Request

from app.dependencies import get_submissions_service
from app.jinja.templates import templates
from app.services.submissions_service import SubmissionsService

router = APIRouter(prefix="/analytics")


@router.get(
    "/",
    name="analytics_form",
    response_class=HTMLResponse
)
async def analytics_page(
        request: Request,
        submissions_service: SubmissionsService = Depends(get_submissions_service)
):
    analytics = await submissions_service.get_analytics()
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            **analytics.model_dump()
        },
        status_code=status.HTTP_200_OK
    )
