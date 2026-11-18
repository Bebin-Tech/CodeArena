from typing import Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StrictInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class EmailInput(StrictInput):
    email: EmailStr = Field(max_length=254)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower()


class PasswordInput(StrictInput):
    password: str = Field(min_length=12, max_length=128)

    @field_validator('password')
    @classmethod
    def strong_password(cls, value):
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError('Use at least one letter and one number.')
        return value


class Register(EmailInput, PasswordInput):
    full_name: str = Field(min_length=2, max_length=120)
    user_type: Literal['student', 'developer', 'candidate'] = 'developer'
    country: str = Field(min_length=2, max_length=80)
    institution: str = Field(default='', max_length=160)


class Login(EmailInput):
    password: str = Field(min_length=1, max_length=128)


class TokenInput(StrictInput):
    token: str = Field(min_length=32, max_length=200)


class ResetPassword(TokenInput, PasswordInput):
    pass


class ProfileInput(StrictInput):
    full_name: str = Field(min_length=2, max_length=120)
    country: str = Field(min_length=2, max_length=80)
    institution: str = Field(default='', max_length=160)
    bio: str = Field(default='', max_length=500)


class UserPublic(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: str
    country: str
    institution: str
    bio: str
    verified: bool
    onboarded: bool
    created_at: datetime


class Message(BaseModel):
    message: str


class SessionPublic(BaseModel):
    id: UUID
    created_at: datetime
    expires_at: datetime
    user_agent: str
    current: bool
