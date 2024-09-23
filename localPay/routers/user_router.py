from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from urllib.parse import quote

from auth.auth_service import AuthService, oauth2_scheme
from auth.check_permissions import (
    check_permissions,
    is_admin_or_supervisor_role,
    is_admin_role,
    is_user_role,
)
from crud.user_service import UserService
from db.database import get_db
from schemas.user import User, UserCreate, UserUpdate
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