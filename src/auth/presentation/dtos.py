import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.auth.domain.exceptions import ValidationErrorPassword


class UserRegisterDTO(BaseModel):
    token_key: str = Field(default=None)
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")
    username: str = Field(min_length=5)

    @field_validator("password", "after")
    async def _validate_password(self, v: str):
        r = re.search("[a-zA-Z0-9$%#@!.?]", v)
        if not r:
            raise ValidationErrorPassword()

        return v


class UserLoginDTO(BaseModel):
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")
    otp_code: str | None = Field(None, description="OTP code is required")
    email_code: int | None = Field(None, description="Email code is required")


class UserOtpVerifyDTO(BaseModel):
    otp_code: str = Field(..., description="OTP code is required")
