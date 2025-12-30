from fastapi import APIRouter, Request
from uuid import UUID

from fastapi.params import Depends
from app.domain.schemas.question_schema import (
    CreateTextQuestionRequest,
    QuestionResponse
)
from app.services.question_service import QuestionService, get_question_service

router = APIRouter(prefix="/forms", tags=["Questions"])

@router.post(
    "/{survey_id}/questions",
    response_model=QuestionResponse,
    status_code=201
)
async def add_text_question(
    survey_id: UUID,
    payload: CreateTextQuestionRequest,
    request: Request,
    service: QuestionService = Depends(get_question_service),

):
    user_id_str = request.state.user_id
    return await service.add_text_question(
        survey_id=survey_id,
        user_id=user_id_str,
        payload=payload,
    )
