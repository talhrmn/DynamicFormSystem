from fastapi import APIRouter

from app.views.v1.data.submissions import router as submissions_router

router = APIRouter(prefix="/data", tags=["Raw Data Endpoints"])

router.include_router(submissions_router)
