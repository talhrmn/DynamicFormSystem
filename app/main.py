from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.common.logger import setup_logging, get_logger
from app.core.config import get_settings
from app.core.system import get_system_manager
from app.database.database import engine
from app.database.dynamic.model_factory import create_dynamic_model
from app.database.dynamic.table_manager import create_table_if_not_exists
from app.views.api import api_router

"""
GLOBALS
"""
settings = get_settings()
system_manager = get_system_manager()

setup_logging()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan
    :param app:
    :return:
    """
    logger.info(
        "startup_begin",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    try:
        # Load schema
        system_manager.load_schema_from_file(f"{settings.SCHEMA_DIR_PATH}/{settings.SCHEMA_FILE_NAME}")
        logger.info("schema_loaded")

        # Create dynamic table
        form_schema = system_manager.get_form_schema()
        DynamicModel = create_dynamic_model(form_schema, table_name="dynamic_form_data")
        await create_table_if_not_exists(DynamicModel, engine)
        system_manager.set_table_model(DynamicModel)
        logger.info("dynamic_table_created")

        yield

    except Exception as e:
        logger.error("startup_failed", error=str(e))
        raise

    finally:
        logger.info("shutdown")


"""
APPLICATION
"""
app = FastAPI(
    title=settings.APP_NAME,
    description="Dynamic for system",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "jinja/static"

if STATIC_DIR.exists():
    app.mount("/jinja/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info("Static files mounted", path=str(STATIC_DIR))
else:
    logger.warning("Static directory not found", path=str(STATIC_DIR))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# API routers
app.include_router(
    api_router,
    responses={
        503: {"description": "Service unavailable"},
        500: {"description": "Internal server error"},
    },
)


# -----------------------------------------------------------------------------
# ROOT ENDPOINT
# -----------------------------------------------------------------------------
@app.get("/", tags=["Root"], summary="API Root")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": {"swagger": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"}
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
