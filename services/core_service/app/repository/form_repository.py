import select
from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.domain.models.servey_model import Survey
from app.domain.models.settings_model import Setting
from app.core.database import get_db


class FormRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # -----------------------------------
    # CREATE SURVEY
    # -----------------------------------
    async def create_survey(
        self, 
        creator_id: str, 
        title: str, 
        slug: str
    ) -> Survey:
        """ساخت فرم جدید با تنظیمات پیش‌فرض"""
        
        # 1. ساخت آبجکت فرم
        new_survey = Survey(
            creator_id=creator_id,
            title=title,
            slug=slug,
            is_public=False
        )
        self.session.add(new_survey)
        
        # 2. فلاش می‌کنیم تا survey_id تولید بشه (ولی هنوز کامیت نمیشه)
        await self.session.flush() 
        logger.info(f"Survey {new_survey.survey_id} created for creator {creator_id}")

        # 3. ساخت تنظیمات پیش‌فرض برای همین فرم
        default_setting = Setting(
            survey_id=new_survey.survey_id
        )
        self.session.add(default_setting)
        
        return new_survey
    
    async def get_forms_by_creator(self, creator_id: UUID):
        stmt = select(Survey).where(
            Survey.creator_id == creator_id
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ---------------------------------------
# DEPENDENCY (برای FastAPI)
# ---------------------------------------
async def get_form_repository(
    session: AsyncSession = Depends(get_db)
) -> FormRepository:
    return FormRepository(session)
