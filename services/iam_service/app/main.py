from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from loguru import logger
from contextlib import asynccontextmanager

from app.api.auth_routes import auth_router
from app.core.config import get_settings
from app.core.database import create_db_and_tables
from app.logging.logging_service import configure_logger
from fastapi.security import HTTPBearer


# ============================================
# 1. Logger
# ============================================
configure_logger()
logger.info("Logger configured.")

settings = get_settings()


# ============================================
# 2. Lifespan
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


# ============================================
# 3. Create FastAPI app FIRST
# ============================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    description="Identity and Access Management (IAM) Service for QForm",
)

logger.info(f"{settings.PROJECT_NAME} v{settings.PROJECT_VERSION} is starting up...")


# ============================================
# 4. Security Scheme (global)
# ============================================
bearer_scheme = HTTPBearer(auto_error=True)   # پیشنهاد قوی


# ============================================
# 5. Custom OpenAPI AFTER app is created
# ============================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="IAM Service",
        version="1.0.0",
        description="Identity and Access Management",
        routes=app.routes,
    )

    # ⭐ اینجا securitySchemes تعریف می‌شود
    openapi_schema["components"]["securitySchemes"] = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
}


    # ⭐ اینجا باعث می‌شود دکمه Authorize در Swagger ظاهر شود
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================
# 6. Middleware
# ============================================
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured with allow_origins: {}", origins)


# ============================================
# 7. Routes
# ============================================
app.include_router(auth_router, prefix="/api/v1")
logger.info("Included auth_router with prefix /api/v1")


# ============================================
# 8. Root Endpoint
# ============================================
@app.get("/", tags=["Health Check"])
async def root():
    logger.debug("Root health check endpoint was hit.")
    return {"status": "ok", "message": "Welcome to QForm IAM Service!"}


logger.success("🚀 IAM Service has started successfully!")
