from typing import Dict, Optional

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
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
from crud.payment_service import PaymentService
from crud.user_service import UserService
from db.database import get_db
from schemas.payment import PaymentUpdate
from schemas.user import RegionEnum
from utils.utils import parse_date, validate_dates, get_payment_service, get_user_service, get_auth_service, \
    get_auth_service

router = APIRouter(tags=["payments"])




@router.get("/payments")
@check_permissions(is_user_role)
def get_all_payments(
        cursor: Optional[int] = None,
        per_page: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        ls_abon: Optional[str] = None,
        name: Optional[str] = None,
        payment_service: PaymentService = Depends(get_payment_service),
        auth_service: AuthService = Depends(get_auth_service),
        token: str = Depends(oauth2_scheme)
):
    payments, total_count, next_cursor = payment_service.get_payments(cursor, per_page, start_date, end_date, ls_abon, name)
    return {"payments": payments, "total": total_count, "next_cursor": next_cursor, "per_page": per_page}


@router.get("/payments_by_user")
@check_permissions(is_user_role)
def get_all_payments_by_user(
        login: str,
        start_date: Optional[str] = Query(None, description="Start date in DD-MM-YYYY format"),
        end_date: Optional[str] = Query(None, description="End date in DD-MM-YYYY format"),
        cursor: Optional[int] = None,
        per_page: int = 10,
        payment_service: PaymentService = Depends(get_payment_service),
        auth_service: AuthService = Depends(get_auth_service),
        token: str = Depends(oauth2_scheme)
):
    print(start_date, end_date)
    payments, total_count, next_cursor = payment_service.single_user_payments(
        login, start_date, end_date, cursor, per_page
    )
    return {"payments": payments, "total": total_count, "next_cursor": next_cursor, "per_page": per_page}


@router.get("/payment_by_id/{id}")
@check_permissions(is_admin_or_supervisor_role)
def get_payment_by_id(
        id: int,
        payment_service: PaymentService = Depends(get_payment_service),
        auth_service: AuthService = Depends(get_auth_service),
        token: str = Depends(oauth2_scheme)):
    return payment_service.get_payment_by_id(id)


@router.post("/create_payment")
@check_permissions(is_user_role)
def create_payment(
        ls_abon,
        money,
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
        payment_service: PaymentService = Depends(get_payment_service)
):
    return payment_service.create_payment(ls_abon, money, token)


@router.patch("/update_payment/{id}")
@check_permissions(is_admin_role)
def update_payment(
        id: int,
        payment: PaymentUpdate,
        payment_service: PaymentService = Depends(get_payment_service),
        auth_service: AuthService = Depends(get_auth_service),
        token: str = Depends(oauth2_scheme)):
    return payment_service.update_payment(id, payment)


@router.get("/export-all-user-payments")
@check_permissions(is_admin_or_supervisor_role)
def export_all_payments(
        start_date: Optional[str] = Query(None, description="Start date in DD-MM-YYYY format"),
        end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
        region: Optional[RegionEnum] = Query(None, description="Region"),
        payment_service: PaymentService = Depends(get_payment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
):
    # start_date = datetime.strptime(start_date, "%d/%m/%Y") if start_date else None
    # end_date = datetime.strptime(end_date, "%d/%m/%Y") if end_date else None

    validate_dates(start_date, end_date)

    output = payment_service.export_all_user_payments(start_date=start_date, end_date=end_date, region=region)
    encoded_name = quote(f"Отчет по оплатам всех пользователей.xlsx")

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_name}"
        }
    )


@router.get("/export-single-user-payments/")
@check_permissions(is_user_role)
def export_single_user_payments(
        user_id: Optional[int] = Query(None, description="User ID"),
        login: Optional[str] = Query(None, description="User login"),
        start_date: Optional[str] = Query(None, description="Start date in DD-MM-YYYY format"),
        end_date: Optional[str] = Query(None, description="End date in DD-MM-YYYY format"),
        payment_service: PaymentService = Depends(get_payment_service),
        user_service: UserService = Depends(get_user_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
):
    if user_id is None and login is None:
        raise HTTPException(status_code=400, detail="Login or User ID are required")

    # start_date = datetime.strptime(start_date, "%d/%m/%Y") if start_date else None
    # end_date = datetime.strptime(end_date, "%d/%m/%Y") if end_date else None

    validate_dates(start_date, end_date)

    name = None
    if user_id is not None:
        db_user = user_service.get_user_by_id(user_id)
        name = db_user.name
    elif login is not None:
        db_user = user_service.get_user_by_login(login)
        name = db_user.name

    output = payment_service.single_user_payment_report(user_id=user_id, login=login, start_date=start_date,
                                                        end_date=end_date)

    encoded_name = quote(f"Отчет оплат {name}.xlsx")

    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f"attachment; filename*=UTF-8''{encoded_name}"
        }
    )


@router.get("/planup-localpay-comparison")
@check_permissions(is_user_role)
def planup_localpay_comparison(
        login: str,
        start_date: Optional[str] = Query(None, description="Start date in DD-MM-YYYY format"),
        end_date: Optional[str] = Query(None, description="End date in DD-MM-YYYY format"),
        payment_service: PaymentService = Depends(get_payment_service),
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service)
):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)

    report, full_name = payment_service.planup_localpay_compare(login, start_date, end_date)

    encoded_fullname = quote(f"Отчет оплат {full_name}.xlsx")

    return StreamingResponse(report, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename={encoded_fullname}.xlsx"})


