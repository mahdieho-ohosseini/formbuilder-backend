from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# ورودی (از Modal فرانت)
class CreateFormRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="نام فرم")

# خروجی (پاسخ به فرانت)
class CreateFormResponse(BaseModel):
    survey_id: UUID
    title: str
    slug: str
    is_public: bool = False
    created_at: datetime

    class Config:
        from_attributes = True
