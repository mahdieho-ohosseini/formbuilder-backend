from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    expires_in :int


class TokenDataSchema(BaseModel):
    user_id : int
    is_admin :bool
    is_verified: bool = False