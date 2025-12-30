from uuid import UUID
from fastapi import Depends, HTTPException
from app.repository.question_repository import QuestionRepository, get_question_repository
from app.repository.form_repository import FormRepository, get_form_repository
from app.domain.schemas.question_schema import CreateTextQuestionRequest


class QuestionService:
    def __init__(
        self,
        question_repo: QuestionRepository,
        form_repo: FormRepository,
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
        # Ownership Check
        # -----------------------------------
        form = await self.form_repo.get_owned_form(
            survey_id=survey_id,
            user_id=user_id
        )

        if not form:
            raise HTTPException(
                status_code=404,
                detail="Form not found or you don't have permission"
            )

        # -----------------------------------
        # DUPLICATE CHECK ✅✅✅
        # -----------------------------------
        exists = await self.question_repo.exists_question(
            survey_id=survey_id,
            question_text=payload.question_text,
        )

        if exists:
            raise HTTPException(
                status_code=409,
                detail="Question with same text already exists in this form"
            )

        # -----------------------------------
        # Calculate order_index
        # -----------------------------------
        last_order = await self.question_repo.get_last_order(survey_id)
        order_index = last_order + 1

        # -----------------------------------
        # Create Question
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

        # ✅ Commit نهایی
        await self.question_repo.session.commit()
        await self.question_repo.session.refresh(question)

        return question


# ✅ Dependency Factory با Depends صحیح
def get_question_service(
    question_repo: QuestionRepository = Depends(get_question_repository),
    form_repo: FormRepository = Depends(get_form_repository),
) -> QuestionService:
    return QuestionService(
        question_repo=question_repo,
        form_repo=form_repo,
    )
