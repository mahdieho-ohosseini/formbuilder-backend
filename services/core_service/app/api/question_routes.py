from fastapi import APIRouter, Request
from uuid import UUID
from schemas.question_schema import (
    CreateTextQuestionRequest,
    QuestionResponse
)
from services.question_service import QuestionService

router = APIRouter(tags=["Questions"])

@router.post(
    "/forms/{survey_id}/questions",
    response_model=QuestionResponse,
    status_code=201
)
async def add_text_question(
    survey_id: UUID,
    payload: CreateTextQuestionRequest,
    request: Request,
):
    user_id = request.state.user_id
    return await QuestionService.add_text_question(
        survey_id=survey_id,
        user_id=user_id,
        payload=payload,
    )
