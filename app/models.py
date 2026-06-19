from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    created_at: Optional[datetime] = None


class ResearchLogCreate(BaseModel):
    user_id: str
    topic: str
    summary: str
    execution_time: float


class ResearchLogResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    topic: str
    summary: str
    execution_time: float
    created_at: Optional[datetime] = None