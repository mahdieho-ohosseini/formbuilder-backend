from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from typing import Annotated, Any

from app.dependencies import get_current_user, get_profile_service
from app.domain.profile_schemas import (
    UserProfileResponse,
    ChangePasswordRequest,
)
from app.services1.profile_service import ProfileService
from app.domain.token_schemas import LogoutRequest
from app.services1.auth_services.logout_service import LogoutService
from app.dependencies import get_logout_service

bearer_scheme = HTTPBearer(auto_error=True)


profile_router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)
from typing import Any

@profile_router.get(
    "/me",
    response_model=UserProfileResponse,
    dependencies=[Depends(bearer_scheme)],
    openapi_extra={"security": [{"BearerAuth": []}]},

)
async def get_profile(
    current_user: Any = Depends(get_current_user),  # ✅ مهم
    service: ProfileService = Depends(get_profile_service),
):
    return await service.get_profile(current_user.user_id)



@profile_router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(bearer_scheme)],
    openapi_extra={"security": [{"BearerAuth": []}]},

)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Any = Depends(get_current_user),  # ✅ حیاتی
    service: ProfileService = Depends(get_profile_service),
):
    await service.change_password(
        current_user.user_id,
        payload.current_password,
        payload.new_password,
    )
    return {
        "success": True,
        "message": "Password changed successfully"
    }



@profile_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user (invalidate refresh token)",
)
async def logout(
    body: LogoutRequest,
    logout_service: Annotated[LogoutService, Depends(get_logout_service)],
):
    await logout_service.logout(body.refresh_token)
    return {"message": "Logged out successfully"}



    
