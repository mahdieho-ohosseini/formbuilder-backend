import httpx
from core.config import IAM_SERVICE_URL

async def get_user_by_id(user_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{IAM_SERVICE_URL}/internal/users/{user_id}")
        return response.json()
