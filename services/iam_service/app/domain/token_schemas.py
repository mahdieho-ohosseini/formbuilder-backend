from datetime import datetime
from typing import Optional
from pydantic import BaseModel

#آن چیزی که به کاربر می‌دهیم)
class TokenSchema(BaseModel):#خروجیِ لاگین
    access_token: str
    token_type: str
    expires_in :int

#برای decode کردن JWT و استخراج user_id
class TokenDataSchema(BaseModel):
    user_id : int
    is_admin :bool
    is_verified: bool = False