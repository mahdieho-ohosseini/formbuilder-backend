from time import time

BLACKLIST_PREFIX = "blacklist:token:"


async def blacklist_token(redis, jti: str, exp: int):
    ttl = exp - int(time())
    if ttl > 0:
        await redis.setex(f"{BLACKLIST_PREFIX}{jti}", ttl, "1")


async def is_token_blacklisted(redis, jti: str) -> bool:
    return await redis.exists(f"{BLACKLIST_PREFIX}{jti}") > 0
