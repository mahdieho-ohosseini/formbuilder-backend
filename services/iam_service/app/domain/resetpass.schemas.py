from pydantic import BaseModel, EmailStr, constr

# Step 1
class PasswordResetStartSchema(BaseModel):
    email: EmailStr

class PasswordResetStartResponse(BaseModel):
    success: bool
    message: str

# Step 2
class PasswordResetVerifySchema(BaseModel):
    email: EmailStr
    otp: constr(min_length=4, max_length=6) # type: ignore

class PasswordResetVerifyResponse(BaseModel):
    success: bool
    message: str

# Step 3
class PasswordResetCompleteSchema(BaseModel):
    email: EmailStr
    new_password: constr(min_length=8) # pyright: ignore[reportInvalidTypeForm]

class PasswordResetCompleteResponse(BaseModel):
    success: bool
    message: str
