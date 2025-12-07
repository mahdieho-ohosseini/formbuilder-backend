from fastapi import Request, HTTPException
from time import time

rate_storage = {}

async def rate_limit(request: Request, call_next):
    ip = request.client.host
    now = time()

    window = 10
    limit = 20

    logs = rate_storage.get(ip, [])
    logs = [t for t in logs if now - t < window]

    if len(logs) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")

    logs.append(now)
    rate_storage[ip] = logs

    return await call_next(request)
