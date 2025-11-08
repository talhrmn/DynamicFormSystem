from fastapi import APIRouter

from app.views.v1.data import router as data_router

router = APIRouter(prefix="/v1", tags=["V1 Routes"])

router.include_router(data_router)
