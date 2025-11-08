from fastapi import APIRouter

from app.views.v1.dashboard.form import router as form_router
from app.views.v1.dashboard.preview import router as preview_router

router = APIRouter(prefix="/jinja", tags=["Jinja2 HTML Forms"])

router.include_router(form_router)
router.include_router(preview_router)
