from pydantic import BaseModel, Field
from uuid import UUID
from typing import List


# -------------------------
# Answer Input
# -------------------------
class TextAnswerInputSchema(BaseModel):
    question_id: UUID
    text_value: str = Field(..., min_length=1)


# -------------------------
# Submit Response
# -------------------------
class SubmitResponseRequest(BaseModel):
    answers: List[TextAnswerInputSchema]


# -------------------------
# Submit Response Result
# -------------------------
class SubmitResponseResponse(BaseModel):
    response_id: UUID
    message: str
