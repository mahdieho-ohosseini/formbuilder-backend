# app/services/jwt_middleware.py

from fastapi import Request, HTTPException
import jwt
from app.core.config import get_settings
import os
from loguru import logger

settings = get_settings()


async def jwt_middleware(request: Request, call_next):
    """
    JWT Middleware for protected routes
    """

    # ✅ 0. Allow CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path

    # ✅ 1. Public routes
    public_routes = (
        "/api/v1/auth",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/health",
    )

    if any(path.startswith(p) for p in public_routes):
        return await call_next(request)

    # ✅ 2. Dev mode bypass
    if os.getenv("DEV_MODE", "false").lower() == "true":
        logger.warning("🚨 DEV_MODE enabled — JWT bypassed")
        request.state.user_id = "00000000-0000-0000-0000-000000000000"
        return await call_next(request)

    # ✅ 3. Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning(f"❌ Missing Authorization header for {path}")
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.split(" ", 1)[1]

    # ✅ 4. Decode & validate token
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # ✅ 5. Token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type (access required)",
            )

        # ✅ 6. Extract user_id
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Token missing subject (sub)",
            )

        request.state.user_id = user_id
        logger.info(f"✅ Authenticated user {user_id} for {path}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ JWT error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return await call_next(request)
