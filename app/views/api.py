from fastapi import APIRouter

from app.core.config import get_settings
from app.views.v1 import router as v1_router

settings = get_settings()

api_router = APIRouter(prefix=settings.API_PREFIX)

api_router.include_router(v1_router)
