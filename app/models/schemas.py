# app/models/schemas.py
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.models.enums import Role, ApplicationStatus


# ---------- Response envelopes ----------
class BaseResponse(BaseModel):
    success: bool
    message: str
    object: Optional[dict] = None
    errors: Optional[List[str]] = None


class PaginatedResponse(BaseModel):
    success: bool
    message: str
    object: list
    page_number: int
    page_size: int
    total_size: int
    errors: Optional[List[str]] = None


# ---------- Auth ----------
class SignUpIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role

    @field_validator("name")
    def name_alpha_spaces(cls, v: str) -> str:
        """
        Accept only letters (any Unicode alphabet) and spaces.
        """
        if not v or not all(ch.isalpha() or ch.isspace() for ch in v):
            raise ValueError("Name must contain only alphabetic characters and spaces")
        return v.strip()

    @field_validator("password")
    def strong_password(cls, v: str) -> str:
        """
        Password strength rules without regex look‑aheads:
          • ≥ 8 characters
          • ≥ 1 lower, ≥ 1 upper, ≥ 1 digit, ≥ 1 special symbol
        """
        specials = "@$!%*#?&"
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain a lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        if not any(c in specials for c in v):
            raise ValueError(f"Password must contain a special character ({specials})")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


# ---------- Auth ----------
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"



# ---------- Job ----------
class JobIn(BaseModel):
    title: str
    description: str
    location: Optional[str] = None

    @field_validator("title")
    def title_length(cls, v: str) -> str:
        if not (1 <= len(v) <= 100):
            raise ValueError("Title must be 1–100 characters long")
        return v

    @field_validator("description")
    def desc_length(cls, v: str) -> str:
        if not (20 <= len(v) <= 2000):
            raise ValueError("Description must be 20–2000 characters long")
        return v


# ---------- Application ----------
class ApplyIn(BaseModel):
    cover_letter: Optional[str] = None

    @field_validator("cover_letter")
    def cover_len(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 200:
            raise ValueError("Cover letter must be ≤ 200 characters")
        return v
