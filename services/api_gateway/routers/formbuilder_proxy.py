from fastapi import APIRouter, Request
import httpx
from core.config import FORMBUILDER_SERVICE_URL

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def formbuilder_proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        body = await request.body()

        response = await client.request(
            method=request.method,
            url=f"{FORMBUILDER_SERVICE_URL}/forms/{path}",
            content=body,
            headers=request.headers
        )

        return response.json()
