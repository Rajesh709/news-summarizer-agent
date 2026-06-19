from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(default="default", min_length=1, max_length=64)


class ChatResponse(BaseModel):
    response: str
    session_id: str


class HealthResponse(BaseModel):
    status: str
    redis: bool
    scheduler_running: bool = False
    next_digest: Optional[str] = None
    version: str = "1.0.0"


class ClearSessionRequest(BaseModel):
    session_id: str


class DigestRequest(BaseModel):
    recipient: Optional[str] = None   # defaults to DIGEST_RECIPIENT in .env


class DigestResponse(BaseModel):
    message: str
    recipient: str
