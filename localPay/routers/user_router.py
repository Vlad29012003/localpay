from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from urllib.parse import quote
import logging
from passlib.context import CryptContext

from passlib.hash import django_pbkdf2_sha256

from auth.auth_service import AuthService, oauth2_scheme
from auth.check_permissions import (
    check_permissions,
    is_admin_or_supervisor_role,
    is_admin_role,
    is_user_role,
)
from crud.user_service import UserService
from db.database import get_db
from schemas.user import User, UserCreate, UserUpdate, AdminChangePasswordRequest
from utils.utils import get_user_service, get_auth_service

router = APIRouter(tags=["users"])



@router.get("/users")
@check_permissions(is_admin_or_supervisor_role)
def get_all_users(
        cursor: Optional[int] = None,
        per_page: int = 10,
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):

    users, total_count, next_cursor = user_service.get_users(cursor, per_page)
    return {"users": users, "total": total_count, "next_cursor": next_cursor, "per_page": per_page}


@router.get("/user_by_id/{id}")
@check_permissions(is_user_role)
def get_user_by_id(
        id: int,
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):

    return user_service.get_user_by_id(id)


@router.get("/user_by_login/{login}")
@check_permissions(is_user_role)
def get_user_by_id(
        login: str,
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):

    return user_service.get_user_by_login(login)


@router.post("/create_user")
# @check_permissions(is_admin_role)
def create_user(
        user: UserCreate,
        user_service: UserService = Depends(get_user_service),
        # token: str = Depends(oauth2_scheme),
        # auth_service: AuthService = Depends(get_auth_service)
        ):
    return user_service.create_user(user)


@router.patch("/update_user/{id}", response_model=User)
@check_permissions(is_admin_role)
def update_user(
        id: int,
        user: UserUpdate,
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):
    return user_service.update_user(id, user)


@router.delete("/delete_user/{id}")
@check_permissions(is_admin_role)
def delete_user(
        id: int,
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):
    return user_service.delete_user(id)


@router.get("/export-all-users-info")
@check_permissions(is_admin_or_supervisor_role)
def export_all_users_info(
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
):

    output = user_service.export_users_info_excel()

    encoded_name = quote(f"Отчет по всем пользователям.xlsx")

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_name}"
        }
    )



def get_password_hash(password: str) -> str:
    return django_pbkdf2_sha256.hash(password)


@router.post("/users/{user_id}/change-password")
def admin_change_user_password(
        user_id: int,
        request: AdminChangePasswordRequest,
        db: Session = Depends(get_db),
        user_service: UserService = Depends(get_user_service)
    ):
    print('************************')
    print(f'User ID: {user_id}')
    print(f'New password: {request.new_password}')
    print(f'Confirm password: {request.confirm_password}')
    print('************************')

    # Проверка, что новый пароль и его подтверждение совпадают
    if not request.passwords_match():
        print(f"Passwords do not match for user {user_id}")
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Хэшируем новый пароль
    hashed_password = get_password_hash(request.new_password)
    print(f"Password hashed for user {user_id}")
    
    # Используем сервис для изменения пароля пользователя
    try:
        print(f"Calling user_service.change_password for user {user_id}")
        user_service.change_password(user_id, hashed_password, db)
        print(f"Password successfully changed for user {user_id}")
        return {"message": "Password changed successfully"}
    except ValueError as e:
        print(f"ValueError occurred while changing password for user {user_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Unexpected error occurred while changing password for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")