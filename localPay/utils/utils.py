from datetime import datetime
from typing import List, Dict, Optional

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from auth.auth_service import AuthService
from crud.comment_service import CommentService
from crud.payment_service import PaymentService
from crud.user_service import UserService
from db.database import get_db



def parse_date(date_str: Optional[str]) -> Optional[str]:
    if date_str:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Wrong date format. Use DD/MM/YYYY")
    return None


def validate_dates(start_date: Optional[str], end_date: Optional[str]) -> None:
    pass


def get_payment_service(db: Session = Depends(get_db)):
    return PaymentService(db)


def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)


def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db=db)


def get_comment_service(db: Session = Depends(get_db)):
    return CommentService(db)