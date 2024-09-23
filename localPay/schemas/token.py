from datetime import datetime
from pydantic import BaseModel

from schemas.user import RoleEnum


class TokenPayload(BaseModel):
    id: int
    role: RoleEnum
    exp: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
