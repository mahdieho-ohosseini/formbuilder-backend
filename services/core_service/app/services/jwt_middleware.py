# app/services/jwt_middleware.py

from fastapi import Request, HTTPException
import jwt
from app.core.config import get_settings
import os
from loguru import logger

settings = get_settings()


async def jwt_middleware(request: Request, call_next):
    """
    Middleware برای بررسی JWT در همه مسیرهای Protected
    """
    path = request.url.path
    
    # 1️⃣ مسیرهای Public
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

    # 2️⃣ Dev mode bypass
    if os.getenv("DEV_MODE", "false").lower() == "true":
        logger.warning("🚨 DEV_MODE is ON - Bypassing JWT check")
        request.state.user_id = "00000000-0000-0000-0000-000000000000"
        return await call_next(request)

    # 3️⃣ بررسی Header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning(f"❌ Missing token for {path}")
        raise HTTPException(
            status_code=401, 
            detail="Missing or invalid Authorization header"
        )

    token = auth_header.split(" ")[1]

    # 4️⃣ Decode و Verify
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        
        # 5️⃣ بررسی نوع توکن
        if payload.get("type") != "access":
            logger.warning(f"❌ Invalid token type: {payload.get('type')}")
            raise HTTPException(
                status_code=401,
                detail="Invalid token type. Expected 'access' token."
            )
        
        # 6️⃣ استخراج user_id
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("❌ Token payload missing 'sub' field")
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
        
        # 7️⃣ ذخیره در request.state
        request.state.user_id = user_id
        logger.info(f"✅ User {user_id} authenticated for {path}")
        
    except HTTPException:
        # اگه خودمون HTTPException انداختیم، بدون تغییر بفرستش بیرون
        raise
        
    except Exception as e:
        # همه خطاهای دیگه (از جمله JWT)
        error_msg = str(e).lower()
        logger.error(f"❌ JWT Error: {e}")
        
        if "expired" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        elif "signature" in error_msg:
            raise HTTPException(
                status_code=401,
                detail="Invalid token signature"
            )
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    # 8️⃣ ادامه درخواست
    return await call_next(request)
