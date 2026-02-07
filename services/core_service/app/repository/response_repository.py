from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from uuid import UUID
from datetime import datetime, timezone  # ✅ timezone رو import کن

from app.domain.models.response_model import Response
from app.domain.models.answer_model import AnswerText


class ResponseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ----------------------------------
    # Create Response Session
    # ----------------------------------
    async def create_response(
        self,
        survey_id: UUID,
        ip_address: str,
        user_agent: str | None,
    ) -> Response:
        response = Response(
            survey_id=survey_id,
            ip_address=ip_address,
            user_agent=user_agent,
            is_complete=False,
            answers_count=0,

        )
        self.session.add(response)
        await self.session.flush()
        return response

    # ----------------------------------
    # Add Text Answer
    # ----------------------------------
    async def add_text_answer(
        self,
        response_id: UUID,
        question_id: UUID,
        text_value: str,
    ):
        answer = AnswerText(
            response_id=response_id,
            question_id=question_id,
            text_value=text_value,
        )
        self.session.add(answer)

    # ----------------------------------
    # Finalize Response
    # ----------------------------------
    async def finalize_response(
        self,
        response: Response,
        answers_count: int,
    ):
        response.is_complete = True
        response.submitted_at = datetime.now(timezone.utc)  # ✅ aware!
        response.answers_count = answers_count
