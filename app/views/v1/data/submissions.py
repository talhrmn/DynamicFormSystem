from fastapi import APIRouter, Depends

from app.dependencies import get_submissions_service
from app.schemas.data.submissions import SubmissionsDataResponse
from app.services.submissions_service import SubmissionsService

router = APIRouter()


@router.get(
    "/",
    response_model=SubmissionsDataResponse,
    summary="List all form submissions",
    description="Retrieve all form submissions from the database"
)
async def list_submissions(
        submissions_service: SubmissionsService = Depends(get_submissions_service)
) -> SubmissionsDataResponse:
    """
    Get all form submissions.
    """
    submissions = await submissions_service.get_submissions_data()

    submissions_dicts = [sub.model_dump() for sub in submissions]

    return SubmissionsDataResponse(
        submissions=submissions_dicts,
        total=len(submissions_dicts)
    )
