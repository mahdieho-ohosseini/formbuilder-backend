from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from loguru import logger

from app.domain.models.question_model import Question
from app.core.database import get_db


class QuestionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------------
    # GET LAST ORDER INDEX
    # -----------------------------------
    async def get_last_order(self, survey_id: UUID) -> int:
        stmt = select(
            func.coalesce(func.max(Question.order_index), 0)
        ).where(
            Question.survey_id == survey_id
        )

        result = await self.session.execute(stmt)
        last_order = result.scalar_one()

        logger.debug(
            f"Last order_index for survey {survey_id}: {last_order}"
        )
        return last_order

    # -----------------------------------
    # CREATE QUESTION
    # -----------------------------------
    async def create_question(
        self,
        survey_id: UUID,
        question_text: str,
        description: str | None,
        is_required: bool,
        min_length: int,
        max_length: int,
        order_index: int
    ) -> Question:
        question = Question(
            survey_id=survey_id,
            type="text",
            question_text=question_text,
            description=description,
            is_required=is_required,
            min_length=min_length,
            max_length=max_length,
            order_index=order_index,
        )

        self.session.add(question)

        # flush → id ساخته میشه ولی commit هنوز نداریم
        await self.session.flush()

        logger.info(
            f"Question {question.question_id} created "
            f"for survey {survey_id} at order {order_index}"
        )

        return question


# ---------------------------------------
# DEPENDENCY (برای FastAPI)
# ---------------------------------------
async def get_question_repository(
    session: AsyncSession = Depends(get_db),
) -> QuestionRepository:
    return QuestionRepository(session)
