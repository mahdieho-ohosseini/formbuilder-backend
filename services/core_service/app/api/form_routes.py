from fastapi import APIRouter, Depends, HTTPException, Request, status
from uuid import UUID
from loguru import logger

from app.domain.schemas.form_schema import CreateFormRequest, CreateFormResponse
from app.services.form_service import FormService
from app.repository.form_repository import get_form_repository, FormRepository

router = APIRouter(prefix="/forms", tags=["Form Builder"])


@router.post(
    "/create",
    response_model=CreateFormResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_form(
    request: Request,
    payload: CreateFormRequest,
    form_repository: FormRepository = Depends(get_form_repository)
):
    """
    🎯 API برای ساخت فرم جدید
        """
    # 1️⃣ گرفتن user_id از request.state (که Middleware ست کرده)
    user_id_str = request.state.user_id
    
    # 2️⃣ تبدیل به UUID (اگه string بود)
    try:
        creator_id = UUID(user_id_str) if isinstance(user_id_str, str) else user_id_str
    except ValueError:
        logger.error(f"❌ Invalid UUID format: {user_id_str}")
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID format"
        )
    
    logger.info(f"📝 Creating form for user {creator_id}")
    
    # 3️⃣ راه‌اندازی سرویس
    service = FormService(repository=form_repository)
    
    # 4️⃣ ساخت فرم
    new_survey = await service.create_new_form(
        creator_id=creator_id,
        title=payload.title,

    )
    
    logger.info(f"✅ Form created: {new_survey.survey_id}")
    
    # 5️⃣ بازگشت پاسخ
    return CreateFormResponse(
        survey_id=new_survey.survey_id,
        title=new_survey.title,
        slug=new_survey.slug,
        status="PUBLISHED" if new_survey.is_public else "DRAFT",
        created_at=new_survey.created_at
    )



