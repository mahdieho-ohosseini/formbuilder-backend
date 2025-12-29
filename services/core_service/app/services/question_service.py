from uuid import UUID
from fastapi import HTTPException, Depends

from app.repository.question_repository import QuestionRepository
from app.repository.form_repository import FormRepository
from app.domain.schemas.question_schema import CreateTextQuestionRequest


class QuestionService:
    def __init__(
        self,
        question_repo: QuestionRepository = Depends(),
        form_repo: FormRepository = Depends(),
    ):
        self.question_repo = question_repo
        self.form_repo = form_repo

    async def add_text_question(
        self,
        survey_id: UUID,
        user_id: UUID,
        payload: CreateTextQuestionRequest,
    ):
        # -----------------------------------
        # ✅ Ownership Check
        # -----------------------------------
        form = await self.form_repo.get_owned_form(
            survey_id=survey_id,
            user_id=user_id
        )

        if not form:
            raise HTTPException(
                status_code=404,
                detail="Form not found"
            )

        # -----------------------------------
        # ✅ Calculate order_index
        # -----------------------------------
        last_order = await self.question_repo.get_last_order(survey_id)
        order_index = last_order + 1

        # -----------------------------------
        # ✅ Create Question
        # -----------------------------------
        question = await self.question_repo.create_question(
            survey_id=survey_id,
            question_text=payload.question_text,
            description=payload.description,
            is_required=payload.is_required,
            min_length=payload.min_length,
            max_length=payload.max_length,
            order_index=order_index,
        )

        return question
