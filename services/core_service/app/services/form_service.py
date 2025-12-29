import uuid
from loguru import logger
from fastapi import Depends

from app.repository.form_repository import FormRepository, get_form_repository



class FormService:
    def __init__(
        self, 
        repository: FormRepository = Depends(get_form_repository)
    ):
        self.repository = repository

    async def create_new_form(self, creator_id: str, title: str):
        """ساخت فرم جدید با اسلاگ یکتا"""
        
        logger.info(f"Creating new form '{title}' for creator {creator_id}")
        
        # 1. تولید اسلاگ یکتا
        slug = self._generate_slug(title)
        logger.debug(f"Generated slug: {slug}")
        
        # 2. فراخوانی Repository (دیگه db نمیفرستیم)
        survey = await self.repository.create_survey(
            creator_id=creator_id,
            title=title,
            slug=slug
        )
        
        # 3. کامیت نهایی (از session داخل repository)
        await self.repository.session.commit()
        await self.repository.session.refresh(survey)
        
        logger.info(f"Form {survey.survey_id} created successfully")
        return survey

    def _generate_slug(self, title: str) -> str:
        """تولید اسلاگ یکتا از عنوان"""
        safe_title = title.strip().replace(" ", "-")[:50]
        random_suffix = uuid.uuid4().hex[:6]
        return f"{safe_title}-{random_suffix}"
    

    async def get_my_forms(self, creator_id: uuid.UUID):
        return await self.repository.get_forms_by_creator(creator_id)

    
    
