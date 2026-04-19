from fastapi import Form, Body
from pydantic import BaseModel, EmailStr, Field


class UserRegisterDTO(BaseModel):
    token_key: str = Field(default=None)
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")


class UserLoginDTO(BaseModel):
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")
    otp_code: str | None = Field(None, description="OTP code is required")
    email_code: int | None = Field(None, description="Email code is required")


class UserOtpVerifyDTO(BaseModel):
    otp_code: str = Field(..., description="OTP code is required")