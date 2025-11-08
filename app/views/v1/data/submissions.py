from fastapi import APIRouter, Depends

from app.dependencies import get_submissions_service
from app.schemas.data.submissions import SubmissionsDataResponse, DuplicatesResponse, StatsResponse
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


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get basic submission stats",
    description="Retrieve basic statistics of submissions from the database"
)
async def get_stats(
        submissions_service: SubmissionsService = Depends(get_submissions_service),
):
    """
    Return stats about submissions based on the dynamic fields.
    """
    field_stats = await submissions_service.get_field_stats()

    return StatsResponse(
        total_fields=len(field_stats),
        fields=field_stats
    )


@router.get(
    "/duplicates",
    response_model=DuplicatesResponse,
    summary="Get duplicate submissions",
    description="Retrieve all duplicate submissions from the database"
)
async def get_duplicates(
        submissions_service: SubmissionsService = Depends(get_submissions_service),
):
    """
    Return duplicate submissions based on given fields.
    """
    duplicates = await submissions_service.get_duplicates(key_fields=None)
    return DuplicatesResponse(total_groups=len(duplicates), duplicates=duplicates)
