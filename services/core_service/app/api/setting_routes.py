from fastapi import APIRouter, Depends, Request
from uuid import UUID

from app.domain.schemas.setting_schema import (
    SettingResponseSchema,
    SettingUpdateSchema
)
from app.services.setting_service import SettingService
from app.services.setting_service import get_setting_service

router = APIRouter(
    prefix="/forms",
    tags=["Survey Settings"]
)


@router.get(
    "/{survey_id}/settings",
    response_model=SettingResponseSchema,
)
async def get_survey_settings(
    survey_id: UUID,
    request: Request,
    service: SettingService = Depends(get_setting_service),
):
    user_id: UUID = request.state.user_id

    return await service.get_settings(
        survey_id=survey_id,
        user_id=user_id,
    )


@router.patch(
    "/{survey_id}/settings",
    response_model=SettingResponseSchema,
)
async def update_survey_settings(
    survey_id: UUID,
    data: SettingUpdateSchema,
    request: Request,
    service: SettingService = Depends(get_setting_service),
):
    user_id: UUID = request.state.user_id

    return await service.update_settings(
        survey_id=survey_id,
        user_id=user_id,
        data=data.model_dump(exclude_unset=True),
    )
