from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repository.response_repository import ResponseRepository
from app.repository.form_repository import FormRepository
from app.repository.question_repository import QuestionRepository
from app.repository.setting_repository import SettingRepository
from app.services.public_response_service import PublicResponseService
from app.domain.schemas.public_response_schema import (
    SubmitResponseRequest,
    SubmitResponseResponse,
)

router = APIRouter(
    prefix="/public/forms",
    tags=["Public Responses"],
)


@router.post("/s/{code}/responses", response_model=SubmitResponseResponse)
async def submit_response(
    code: str,
    payload: SubmitResponseRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = PublicResponseService(
        response_repo=ResponseRepository(db),
        form_repo=FormRepository(db),
        question_repo=QuestionRepository(db),
        setting_repo=SettingRepository(db),
    )

    response = await service.submit_response(
        code=code,
        payload=payload,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    return SubmitResponseResponse(
        response_id=response.response_id,
        message="Response submitted successfully",
    )
