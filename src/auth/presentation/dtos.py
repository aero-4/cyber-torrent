from fastapi import Form, Body
from pydantic import BaseModel, EmailStr, Field


class UserRegisterDTO(BaseModel):
    token_key: str = Field(default=None)
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")


class UserLoginDTO(BaseModel):
    email: EmailStr = Field(min_length=5, description="Email is required")
    password: str = Field(min_length=5, description="Password is required")
    otp_code: str | None = Field(..., description="OTP code is required")


class UserOtpVerifyDTO(BaseModel):
    email: EmailStr = Field(min_length=5, description="Email is required")
    otp_code: str = Field(..., description="OTP code is required")