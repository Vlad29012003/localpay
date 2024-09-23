from typing import Union
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from secrets import token_urlsafe
from sqlalchemy.orm import Session

from config import (
    access_token_expires_minutes,
    algorithm,
    refresh_token_expire_days,
    secret_key,
)
from crud.user_service import UserService
from exceptions.exceptions import UserNotFoundException
from logs.logger_service import LoggerService
from models.refresh_token import RefreshToken
from models.user import User
from passlib.context import CryptContext
from schemas import token as token_schem
from schemas.token import TokenPayload, TokenResponse
from schemas.user import RoleEnum
from passlib.hash import django_pbkdf2_sha256

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

log_service = LoggerService("logs/auth_service")    
success_logger, error_logger = log_service.configure_loggers("auth_service_success", "auth_service_error")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = pwd_context
        self.SECRET_KEY = secret_key
        self.ALGORITHM = algorithm
        self.UserService = UserService(db=db)
        self.ALLOWED = "allowed"
        self.DENIED = "denied"

    def authenticate_user(self, login: str, password: str):
        try:
            user = self.UserService.get_user_by_login(login)
            print(user.hashed_password)
            print(777777777)
            if not user or not django_pbkdf2_sha256.verify(password, user.hashed_password):  # Используем hashed_password
                success_logger.info(f"Failed login attempt for user: {login}")
                return None
            print(user)
            print(11111111111111111111111111111111111111111)
            success_logger.info(f"User {login} authenticated successfully")
            return user
        except Exception as e:
            error_logger.error(f"Error during authentication for user {login}: {str(e)}")
            raise e

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=15)

            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
            success_logger.info(f"Access token created for data: {data}")
            return encoded_jwt
        except Exception as e:
            error_logger.error(f"Error creating access token: {str(e)}")
            raise e

    def create_refresh_token(self, user_id: int):
        try:
            expires_at = datetime.utcnow() + timedelta(days=refresh_token_expire_days)
            token = token_urlsafe(32)
            refresh_token = RefreshToken(
                token=token,
                expires_at=expires_at,
                user_id=user_id
            )
            self.db.add(refresh_token)
            self.db.commit()
            success_logger.info(f"Refresh token created for user ID: {user_id}")
            return token
        except Exception as e:
            error_logger.error(f"Error creating refresh token for user ID {user_id}: {str(e)}")
            raise e


    def login(self, login: str, password: str):
        print(f'{login} --  {password}')
        try:
            user = self.authenticate_user(login, password)
            if not user:
                success_logger.info(f"Login failed for user: {login}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = self.create_access_token(data={"id": user.id, "role": user.role})
            refresh_token = self.create_refresh_token(user.id)
            success_logger.info(f"User {login} logged in successfully")
            return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
        except Exception as e:
            error_logger.error(f"Error during login for user {login}: {str(e)}")
            raise e

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        try:
            db_token = self.db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.revoked == False).first()

            if not db_token or db_token.expires_at < datetime.utcnow():
                error_logger.warning(f"Invalid or expired refresh token: {refresh_token}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user = db_token.user
            new_access_token = self.create_access_token(data={"id": user.id, "role": user.role})
            new_refresh_token = self.create_refresh_token(user.id)

            db_token.revoked = True
            self.db.commit()
            success_logger.info(f"Refresh token refreshed for user ID: {user.id}")
            return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")
        except Exception as e:
            error_logger.error(f"Error refreshing token: {str(e)}")
            raise e

    def revoke_token(self, refresh_token: str):
        try:
            db_token = self.db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
            if not db_token:
                error_logger.warning(f"Invalid token: {refresh_token}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            db_token.revoked = True
            self.db.commit()
            success_logger.info(f"Refresh token revoked: {refresh_token}")
            return True
        except Exception as e:
            error_logger.error(f"Error revoking token: {str(e)}")
            raise e

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            success_logger.info(f"Token verified successfully: {token}")
            return TokenPayload(**payload)
        except JWTError:
            error_logger.error(f"Invalid token: {token}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = self.verify_token(token)
            user = self.db.query(User).filter(User.id == payload.id).first()
            if user is None:
                error_logger.warning(f"User not found for token: {token}")
                raise UserNotFoundException(payload.id)
            success_logger.info(f"Current user fetched successfully: {user.id}")
            return user
        except Exception as e:
            error_logger.error(f"Error fetching current user: {str(e)}")
            raise e

    def check_if_admin(self, user_id: int):
        try:
            role = self.UserService.get_user_by_id(user_id).role
            success_logger.info(f"Checked if user ID {user_id} is admin")
            return role == RoleEnum.ADMIN
        except Exception as e:
            error_logger.error(f"Error checking if user ID {user_id} is admin: {str(e)}")
            raise e

    def check_if_supervisor(self, user_id: int):
        try:
            role = self.UserService.get_user_by_id(user_id).role
            success_logger.info(f"Checked if user ID {user_id} is supervisor")
            return role == RoleEnum.SUPERVISOR
        except Exception as e:
            error_logger.error(f"Error checking if user ID {user_id} is supervisor: {str(e)}")
            raise e

    def get_user_permission(self, current_user: User = Depends(get_current_user)):
        try:
            role = self.UserService.get_user_by_id(current_user.id).role
            if role in [RoleEnum.USER, RoleEnum.ADMIN, RoleEnum.SUPERVISOR]:
                success_logger.info(f"Permission granted for user ID {current_user.id}")
                return self.ALLOWED
            success_logger.info(f"Permission denied for user ID {current_user.id}")
            return self.DENIED
        except Exception as e:
            error_logger.error(f"Error getting permission for user ID {current_user.id}: {str(e)}")
            raise e

    def get_admin_permission(self, current_user: User = Depends(get_current_user)):
        try:
            if self.check_if_admin(current_user.id):
                success_logger.info(f"Admin permission granted for user ID {current_user.id}")
                return self.ALLOWED
            success_logger.info(f"Admin permission denied for user ID {current_user.id}")
            return self.DENIED
        except Exception as e:
            error_logger.error(f"Error getting admin permission for user ID {current_user.id}: {str(e)}")
            raise e

    def get_admin_or_supervisor_permission(self, current_user: User = Depends(get_current_user)):
        try:
            if self.check_if_admin(current_user.id) or self.check_if_supervisor(current_user.id):
                success_logger.info(f"Admin or supervisor permission granted for user ID {current_user.id}")
                return self.ALLOWED
            success_logger.info(f"Admin or supervisor permission denied for user ID {current_user.id}")
            return self.DENIED
        except Exception as e:
            error_logger.error(f"Error getting admin or supervisor permission for user ID {current_user.id}: {str(e)}")
            raise e
