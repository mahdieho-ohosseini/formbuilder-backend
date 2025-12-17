from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from typing import Annotated, Any

from app.dependencies import get_current_user, get_profile_service
from app.domain.profile_schemas import (
    UserProfileResponse,
    ChangePasswordRequest,
)
from app.services1.profile_service import ProfileService

bearer_scheme = HTTPBearer(auto_error=True)

profile_router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
    dependencies=[Depends(bearer_scheme)],
)
from typing import Any

@profile_router.get(
    "/me",
    response_model=UserProfileResponse,
)
async def get_profile(
    current_user: Any = Depends(get_current_user),  # ✅ مهم
    service: ProfileService = Depends(get_profile_service),
):
    return await service.get_profile(current_user.id)



@profile_router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Any = Depends(get_current_user),  # ✅ حیاتی
    service: ProfileService = Depends(get_profile_service),
):
    await service.change_password(
        current_user.id,
        payload.current_password,
        payload.new_password,
    )
    return {
        "success": True,
        "message": "Password changed successfully"
    }

    
