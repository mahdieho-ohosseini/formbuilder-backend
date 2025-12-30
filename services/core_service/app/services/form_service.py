import uuid
from loguru import logger
from fastapi import Depends, HTTPException, status
from uuid import UUID

from app.repository.form_repository import FormRepository, get_form_repository


class FormService:
    def __init__(
        self,
        repository: FormRepository = Depends(get_form_repository)
    ):
        self.repository = repository

    async def create_new_form(self, creator_id: UUID, title: str):
        logger.info(f"Creating new form '{title}' for creator {creator_id}")

        # ✅ 1. چک تکراری بودن فرم
        existing = await self.repository.get_by_creator_and_title(
            creator_id=creator_id,
            title=title
        )

        if existing:
            logger.warning(
                f"Duplicate form attempt by creator {creator_id} for title '{title}'"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a form with this title"
            )

        # ✅ 2. تولید اسلاگ یکتا
        slug = self._generate_slug(title)
        logger.debug(f"Generated slug: {slug}")

        # ✅ 3. ساخت فرم
        survey = await self.repository.create_survey(
            creator_id=creator_id,
            title=title,
            slug=slug
        )

        # ✅ 4. commit نهایی
        try:
            await self.repository.session.commit()
        except Exception:
            await self.repository.session.rollback()
            raise

        await self.repository.session.refresh(survey)

        logger.info(f"Form {survey.survey_id} created successfully")
        return survey

    def _generate_slug(self, title: str) -> str:
        safe_title = title.strip().replace(" ", "-")[:50]
        random_suffix = uuid.uuid4().hex[:6]
        return f"{safe_title}-{random_suffix}"

    async def get_my_forms(self, creator_id: UUID):
        return await self.repository.get_forms_by_creator(creator_id)
