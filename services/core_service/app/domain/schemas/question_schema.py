from pydantic import BaseModel, Field
from typing import Optional

class CreateTextQuestionRequest(BaseModel):
    question_text: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_required: bool = True
    min_length: int = 0
    max_length: int = 255


class QuestionResponse(BaseModel):
    question_id: str
    survey_id: str
    type: str
    question_text: str
    description: Optional[str]
    is_required: bool
    order_index: int

    class Config:
        from_attributes = True
