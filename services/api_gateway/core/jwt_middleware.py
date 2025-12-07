from fastapi import Request, HTTPException
import jwt
from core.config import JWT_SECRET, JWT_ALGORITHM

async def jwt_middleware(request: Request, call_next):
    path = request.url.path

    public_routes = [
        "/auth/login",
        "/auth/register",
        "/auth/verify-otp"
    ]

    if any(path.startswith(p) for p in public_routes):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]

    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return await call_next(request)
