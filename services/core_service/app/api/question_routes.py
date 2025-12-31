from fastapi import APIRouter, Request
from uuid import UUID

from fastapi.params import Depends
from app.domain.schemas.question_schema import (
    CreateTextQuestionRequest,
    DeleteQuestionResponse,
    QuestionListResponse,
    QuestionResponse
)
from app.services.question_service import QuestionService, get_question_service

router = APIRouter(prefix="/forms", tags=["Questions"])

@router.post(
    "/{survey_id}/add_question",
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


#------------------------------------------------------
@router.delete(
    "/{survey_id}/questions/{question_id}",
    response_model=DeleteQuestionResponse,
    status_code=200,
)
async def delete_question(
    survey_id: UUID,
    question_id: UUID,
    request: Request,
    service: QuestionService = Depends(get_question_service),
):
    user_id = request.state.user_id

    return await service.delete_question(
        survey_id=survey_id,
        question_id=question_id,
        user_id=user_id,
    )
#----------------------------------------------------
@router.get(
    "/{survey_id}/questions",
    response_model=QuestionListResponse,
    summary="List questions of a form"
)
async def list_questions(
    survey_id: UUID,
    request: Request,
    service: QuestionService = Depends(get_question_service),
):
    user_id: UUID = request.state.user_id

    return await service.list_questions(
        survey_id=survey_id,
        user_id=user_id
    )

    
