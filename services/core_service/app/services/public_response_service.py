from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timezone

from app.repository.response_repository import ResponseRepository
from app.repository.form_repository import FormRepository
from app.repository.question_repository import QuestionRepository
from app.repository.setting_repository import SettingRepository


class PublicResponseService:
    def __init__(
        self,
        response_repo: ResponseRepository,
        form_repo: FormRepository,
        question_repo: QuestionRepository,
        setting_repo: SettingRepository,
    ):
        self.response_repo = response_repo
        self.form_repo = form_repo
        self.question_repo = question_repo
        self.setting_repo = setting_repo

    async def submit_response(
        self,
        *,
        code: str,  # ✅ تغییر نام به short_url
        payload,
        ip_address: str,
        user_agent: str | None,
    ):
        # ✅ Load form by short URL
        form = await self.form_repo.get_by_public_code(code)
        if not form:
            raise HTTPException(404, "Form not found")

        # ✅ Load settings
        setting = await self.setting_repo.get_by_survey_id(form.survey_id)
        if not setting or not setting.is_active:
            raise HTTPException(403, "Form is not active")

        # ✅ Date validation
        now = datetime.now(timezone.utc)
        
        if setting.start_date:
            start_aware = setting.start_date
            if start_aware.tzinfo is None:
                start_aware = start_aware.replace(tzinfo=timezone.utc)
            
            if now < start_aware:
                raise HTTPException(400, "Form has not started yet")
        
        if setting.end_date:
            end_aware = setting.end_date
            if end_aware.tzinfo is None:
                end_aware = end_aware.replace(tzinfo=timezone.utc)
            
            if now > end_aware:
                raise HTTPException(400, "Form has expired")

        # ✅ Create response session
        response = await self.response_repo.create_response(
            survey_id=form.survey_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # ✅ Validate & save answers
        questions = await self.question_repo.list_by_survey_id(form.survey_id)
        question_map = {q.question_id: q for q in questions}

        for ans in payload.answers:
            question = question_map.get(ans.question_id)
            if not question:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid question_id: {ans.question_id}",
                )
            value = (ans.text_value or "").strip()
            if question.is_required and not value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Question {question.question_id} is required",
                )

            await self.response_repo.add_text_answer(
                response_id=response.response_id,
                question_id=ans.question_id,
                text_value=ans.text_value,
            )

        # ✅ Finalize
        await self.response_repo.finalize_response(
            response=response,
            answers_count=len(payload.answers),
        )

        await self.response_repo.session.commit()

        return response
