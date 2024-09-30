from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.auth_service import AuthService
from config import access_token_expires_minutes
from db.database import get_db
from schemas.token import RefreshTokenRequest, TokenResponse
from utils.utils import get_auth_service

router = APIRouter(tags=["Auth"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = access_token_expires_minutes


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(form_data.username, form_data.password)


@router.get("/verify-token/{token}")
async def verify_user_token(token: str, auth_service: AuthService = Depends(get_auth_service)):
    print(f"Received token: {token}")
    try:
        current_user = auth_service.get_current_user(token=token)
        return {"message": "Token is valid", "login": current_user.login, "role": current_user.role}
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        raise e


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.refresh_tokens(refresh_data.refresh_token)


@router.post("/revoke")
def revoke_token(refresh_data: RefreshTokenRequest, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.revoke_token(refresh_data.refresh_token)
    return {"message": "Token revoked successfully"}