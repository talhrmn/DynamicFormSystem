from fastapi import Depends, Request, Query, APIRouter
from fastapi.responses import HTMLResponse

from app.dependencies import get_submissions_service
from app.jinja.templates import templates
from app.services.submissions_service import SubmissionsService

router = APIRouter(prefix="/submissions")


@router.get(
    "/",
    name="submissions_form",
    response_class=HTMLResponse
)
async def list_submissions(
        request: Request,
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        sort_by: str = Query("created_at"),
        sort_desc: bool = Query(True),
        submissions_service: SubmissionsService = Depends(get_submissions_service),
):
    """
    List all form submissions with pagination, sorting, and filtering.
    """
    result = await submissions_service.get_submissions(
        query_params=request.query_params.multi_items(),
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_desc=sort_desc,
    )

    return templates.TemplateResponse(
        "submissions.html",
        {
            "request": request,
            **result.model_dump(),
            "query_params": dict(request.query_params)
        }
    )
