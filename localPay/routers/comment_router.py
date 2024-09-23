from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.auth_service import AuthService, oauth2_scheme
from auth.check_permissions import (
    check_permissions,
    is_admin_or_supervisor_role,
    is_admin_role,
    is_user_role,
)
from crud.comment_service import CommentService
from db.database import get_db
from schemas.comment import Comment, CommentCreate, CommentUpdate
from utils.utils import get_comment_service, get_auth_service

router = APIRouter(tags=["comments"])



@router.get("/comments")
@check_permissions(is_admin_or_supervisor_role)
def get_all_comments(
       cursor: Optional[int] = None,
        per_page: int = 10,
        comment_service: CommentService = Depends(get_comment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):

    comments, total_count, next_cursor = comment_service.get_comments(cursor, per_page)
    return {"comments": comments, "total": total_count, "next_cursor": next_cursor, "per_page": per_page}


@router.get("/comment_by_id/{id}", response_model=Comment)
@check_permissions(is_admin_or_supervisor_role)
def get_comment_by_id(
        id: int,
        comment_service: CommentService = Depends(get_comment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):
    return comment_service.get_comment_by_id(id)


@router.post("/create_comment", response_model=Comment)
@check_permissions(is_user_role)
def create_comment(
        comment: CommentCreate,
        comment_service: CommentService = Depends(get_comment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):
    return comment_service.create_comment(comment)


@router.patch("/update_comment/{id}", response_model=Comment)
@check_permissions(is_admin_role)
def update_comment(
        id: int,
        comment: CommentUpdate,
        comment_service: CommentService = Depends(get_comment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):
    return comment_service.update_comment(id, comment)


@router.delete("/delete_comment/{id}")
@check_permissions(is_admin_role)
def delete_comment(
        id: int,
        comment_service: CommentService = Depends(get_comment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)):
    return comment_service.delete_comment(id)