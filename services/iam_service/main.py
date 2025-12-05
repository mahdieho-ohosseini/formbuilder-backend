from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# ===================================================================
# 1. Import local modules (Core, Config, Routes)
# ===================================================================
# مسیر ایمپورت auth_router را با ساختار پروژه خودت تطبیق بده
# این مسیر بر اساس آخرین صحبت‌های ماست
from app.api.auth_routes import auth_router
from app.core.config import get_settings
from app.core.database import init_db  # فرض بر اینکه این تابع برای راه‌اندازی اولیه است
from app.logging.logging_service import configure_logger

# ===================================================================
# 2. Initial Application Setup
# ===================================================================
# راه‌اندازی لاگر در اولین قدم
configure_logger()
logger.info("Logger configured.")

# راه‌اندازی دیتابیس (نکته مهم در توضیحات پایین)
# init_db()  # کامنت شد - در توضیحات بخون چرا
logger.info("Database setup initiated (if applicable).")

# دریافت تنظیمات از config
settings = get_settings()

# ساخت اپلیکیشن FastAPI با اطلاعات تکمیلی برای مستندات
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Identity and Access Management (IAM) Service for QForm"
)
logger.info(f"{settings.PROJECT_NAME} v{settings.PROJECT_VERSION} is starting up...")

# ===================================================================
# 3. Middleware Configuration
# ===================================================================
# نکته امنیتی: در محیط پروداکشن، به جای "*" آدرس دقیق فرانت‌اند را قرار بده
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured with allow_origins: {}", origins)


# ===================================================================
# 4. Include Routers
# ===================================================================
# اضافه کردن روتر احراز هویت با یک پیشوند کلی برای تمام API های ورژن 1
app.include_router(auth_router, prefix="/api/v1")
logger.info("Included auth_router with prefix /api/v1")


# ===================================================================
# 5. Root Endpoint (Health Check)
# ===================================================================
@app.get("/", tags=["Health Check"])
async def root():
    """A simple health check endpoint to confirm the service is running."""
    logger.debug("Root health check endpoint was hit.")
    return {"status": "ok", "message": "Welcome to QForm IAM Service!"}

# این لاگ در زمان استارتاپ یک بار اجرا می‌شود
logger.success("🚀 IAM Service has started successfully!")
