from fastapi import APIRouter

from app.core.config import get_settings
from app.views.v1.data import router as data_router

settings = get_settings()

api_router = APIRouter(prefix=settings.API_PREFIX)

api_router.include_router(data_router)
