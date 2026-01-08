from fastapi import Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.repository.setting_repository import SettingRepository


class SettingService:

    def __init__(self, repository: SettingRepository):
        self.repository = repository

    async def get_settings(self, survey_id: UUID):
        setting = await self.repository.get_by_survey_id(survey_id)

        if not setting:
            setting = await self.repository.create_default(survey_id)

        return setting

    async def update_settings(self, survey_id: UUID, data: dict):
        setting = await self.repository.get_by_survey_id(survey_id)

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found for this survey"
            )

        # ✅ منطق مهم (اختیاری ولی حرفه‌ای)
        if data.get("start_date") and data.get("end_date"):
            if data["start_date"] >= data["end_date"]:
                raise HTTPException(
                    status_code=400,
                    detail="start_date must be before end_date"
                )

        return await self.repository.update(setting, data)


def get_setting_service(
    db: AsyncSession = Depends(get_db),
) -> SettingService:
    repo = SettingRepository(db)
    return SettingService(repo)