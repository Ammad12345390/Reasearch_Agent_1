from pydantic import BaseModel, EmailStr
from typing import Optional


# ---------------- AUTH ----------------

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    email: EmailStr


# ---------------- USER ----------------

class UserResponse(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr


# ---------------- RESEARCH ----------------

class TopicRequest(BaseModel):
    topic: str


class TopicResponse(BaseModel):
    summary: str
    execution_time: float