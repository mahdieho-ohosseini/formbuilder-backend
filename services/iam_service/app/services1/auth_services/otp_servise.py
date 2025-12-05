import random
import string
from typing import Annotated
from fastapi import Depends
from app.services1.auth_services.email_service import get_email_service
# اگر ردیس رو از جای دیگه ایمپورت می‌کنی اینجا تنظیم کن
from app.core.redis import get_redis_client 

class OTPService:
    def __init__(
        self,
        redis_client: Annotated[any, Depends(get_redis_client)],
        email_service: Annotated[any, Depends(get_email_service)]
    ):
        self.redis = redis_client
        self.email_service = email_service

    def _generate_otp(self) -> str:
        """Generate a 6-digit random numeric OTP."""
        return "".join(random.choices(string.digits, k=4)) # یا 6 رقم

    async def send_otp(self, email: str) -> str:
        otp = self._generate_otp()
        
        # 1. ذخیره در ردیس (Async)
        # توجه: اگر ردیس سینک است await نگذار، ولی چون گفتی خطای قبلی await بود، پس ردیس درسته.
        await self.redis.setex(f"otp:{email}", 300, otp)
        
        # 2. ارسال ایمیل
        # نکته مهم: اینجا رو تغییر دادم که به جای to=email از آرگومان پوزیشنال استفاده کنه
        # یا اگر مطمئنی اسمش recipient هست، اون رو بنویس.
        # امن‌ترین روش: بدون نام پارامتر بفرستیم (Positional)
        
        await self.email_service.send_email(
            email,                 # آرگومان اول: گیرنده
            "Your OTP Code",       # آرگومان دوم: موضوع
            f"Your verification code is: {otp}"       # آرگومان سوم: متن
        )
        
        return otp

    async def verify_otp(self, email: str, otp: str) -> bool:
        stored_otp = await self.redis.get(f"otp:{email}")
        if not stored_otp:
            return False
        
        # ردیس بایت برمی‌گردونه، باید دیکد بشه
        if isinstance(stored_otp, bytes):
            stored_otp = stored_otp.decode('utf-8')
            
        if stored_otp == otp:
            # بعد از مصرف موفق، پاکش کن (یکبار مصرف)
            await self.redis.delete(f"otp:{email}")
            return True
            
        return False

    async def check_exist(self, email: str) -> bool:
        exists = await self.redis.exists(f"otp:{email}")
        return exists > 0
