from fastapi import APIRouter, Depends
from app.domain.rimport (
    PasswordResetStartSchema,
    PasswordResetVerifySchema,
    PasswordResetCompleteSchema,
)
from app.services1.auth_services.password_reset_service import PasswordResetService

router = APIRouter(prefix="/auth/password-reset", tags=["Auth"])
