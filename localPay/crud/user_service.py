from passlib.hash import django_pbkdf2_sha256
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Optional
import pandas as pd
from io import BytesIO

from crud.comment_service import CommentService
from db.database import get_db
from exceptions.exceptions import (
    DatabaseConnectionException,
    DatabaseQueryException,
    FileExportFailedException,
    InsufficientFundsException,
    InvalidUserDataException,
    UserLoginNotFoundException,
    UserNotFoundException,
    WriteOffExceedsBalanceException,
)
from logs.logger_service import LoggerService
from models.user import User
from schemas.comment import CommentCreate
from schemas.user import UserCreate, UserUpdate

log_service = LoggerService("logs/user_service")
success_logger, error_logger = log_service.configure_loggers("user_service_success", "user_service_error")

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.DEFAULT_VALUE = 0
        self.comment_service = CommentService(db)
        success_logger.info("UserService initialized")

    def get_users(self, cursor: Optional[int] = None, per_page: int = 10):
        try:
            query = self.db.query(User)
            if cursor:
                query = query.filter(User.id > cursor)
            db_users = query.limit(per_page).all()
            next_cursor = db_users[-1].id if db_users else None
            total_count = self.db.query(User).count()
            success_logger.info(f"Retrieved {len(db_users)} users, total count: {total_count}")
            return db_users, total_count, next_cursor
        except Exception as e:
            error_logger.error(f"Error retrieving users: {str(e)}")
            raise DatabaseQueryException(str(e))
        

    def change_password(self, user_id: int, new_hashed_password: str, db: Session):
        db_user = self.get_user_by_id(user_id)
        if db_user is None:
            error_logger.warning(f"User with id {user_id} not found when trying to change password")
            raise UserNotFoundException(user_id)
        
        old_password = db_user.hashed_password
        db_user.hashed_password = new_hashed_password
        
        print(f"Changing password for user {user_id}")
        print(f"Old password hash: {old_password}")
        print(f"New password hash: {new_hashed_password}")
        
        try:
            db.commit()
            db.refresh(db_user)
            print(f"Changed password for user with id {user_id}")
            print(f"Updated password hash in DB: {db_user.hashed_password}")
            return db_user
        except Exception as e:
            db.rollback()
            error_logger.error(f"Error changing password for user {user_id}: {str(e)}")
            raise DatabaseQueryException(str(e))

    def get_user_by_id(self, user_id: int):
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            error_logger.warning(f"User with id {user_id} not found")
            raise UserNotFoundException(user_id)
        success_logger.info(f"Retrieved user with id {user_id}")
        return db_user

    def get_user_by_login(self, login: str):
        db_user = self.db.query(User).filter(User.login == login).first()
        if db_user is None:
            error_logger.warning(f"User with login {login} not found")
            raise UserLoginNotFoundException(login)
        success_logger.info(f"Retrieved user with login {login}")
        return db_user

    def create_user(self, user: UserCreate):
        print(f"Original password for user {user.login}: {user.password}")
        hashed_password = django_pbkdf2_sha256.hash(user.password)
        print(f"Hashed password for user {user.login}: {hashed_password}")
        if user.surname == "admin":
            user.access_to_payments = True
        elif user.role == "supervisor":
            user.access_to_payments = False
        elif user.role == "user":
            user.access_to_payments = True

        new_user = User(
            name=user.name,
            surname=user.surname,
            login=user.login,
            hashed_password=hashed_password,
            role=user.role,
            access_to_payments=user.access_to_payments,
            is_active=user.is_active,
            spent_money=user.spent_money,
            region=user.region,
            refill=user.refill,
            write_off=user.write_off,
            comment=user.comment
        )

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            success_logger.info(f"Created new user with login {new_user.login}")
            return new_user
        except Exception as e:
            self.db.rollback()
            error_logger.error(f"Error creating user: {str(e)}")
            raise InvalidUserDataException(str(e))

    def update_user(self, user_id: int, user: UserUpdate):
        db_user = self.get_user_by_id(user_id)
        refill_before = db_user.refill
        refill_after = user.refill
        write_off_before = db_user.write_off
        write_off_after = user.write_off

        for field in user.dict(exclude_unset=True):
            if hasattr(db_user, field):
                setattr(db_user, field, getattr(user, field))

        if refill_before != refill_after:
            db_user.available_balance += refill_after
            db_user.refill = self.DEFAULT_VALUE
            success_logger.info(f"Refill for user {user_id}: {refill_after}")
            self.create_comment_for_balance_change(db_user, refill_after, "Пополнение с бухгалтерии")

        if write_off_before != write_off_after:
            if write_off_after > db_user.spent_money:
                error_logger.warning(f"Write-off attempt exceeds balance for user {user_id}")
                raise WriteOffExceedsBalanceException()
            db_user.spent_money += write_off_after
            db_user.available_balance += write_off_after
            db_user.write_off = self.DEFAULT_VALUE
            success_logger.info(f"Write-off for user {user_id}: {write_off_after}")
            self.create_comment_for_balance_change(db_user, write_off_after, "Списание с бухгалтерии")

        try:
            self.db.commit()
            self.db.refresh(db_user)
            success_logger.info(f"Updated user with id {user_id}")
            return db_user
        except Exception as e:
            self.db.rollback()
            error_logger.error(f"Error updating user {user_id}: {str(e)}")
            raise DatabaseQueryException(str(e))

    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        try:
            self.db.delete(db_user)
            self.db.commit()
            success_logger.info(f"Deleted user with id {user_id}")
            return {"deleted user": db_user}
        except Exception as e:
            self.db.rollback()
            error_logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise DatabaseQueryException(str(e))

    def export_users_info_excel(self):
        try:
            users = self.db.query(User).all()
            user_info = [{
                'Имя': user.name,
                'Фамилия': user.surname,
                'Логин': user.login,
                'Доступный Баланс': user.available_balance,
                'Потраченно': user.spent_money,
            } for user in users]
            df = pd.DataFrame(user_info)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Информация о пользователях')
            output.seek(0)
            success_logger.info("Exported users info to Excel successfully")
            return output
        except Exception as e:
            error_logger.error(f"Error exporting users info to Excel: {str(e)}")
            raise FileExportFailedException(str(e))

    def authenticate_user(self, login: str, password: str):
        try:
            user = self.get_user_by_login(login)
            if not user or not django_pbkdf2_sha256.verify(password, user.hashed_password):
                success_logger.info(f"Failed login attempt for user: {login}")
                return None
            success_logger.info(f"Successful login for user: {login}")
            return user
        except Exception as e:
            error_logger.error(f"Error authenticating user {login}: {str(e)}")
            return None

    def create_comment_for_balance_change(self, user, amount, payment_type):
        user_id = user.id
        text = user.comment
        old_available_balance = user.available_balance - amount
        old_spent_money = user.spent_money
        add_to_available_balance = amount
        add_to_spent_money = self.DEFAULT_VALUE
        new_available_balance = user.available_balance
        new_spent_money = user.spent_money

        comment_to_create = CommentCreate(
            user_id=user_id,
            text=text,
            payment_type=payment_type,
            old_available_balance=old_available_balance,
            old_spent_money=old_spent_money,
            add_to_available_balance=add_to_available_balance,
            add_to_spent_money=add_to_spent_money,
            new_available_balance=new_available_balance,
            new_spent_money=new_spent_money
        )

        self.comment_service.create_comment(comment_to_create)



    def delete_user(self, user_id: int):
        db_user = self.get_user_by_id(user_id)
        try:
            self.db.delete(db_user)
            self.db.commit()
            success_logger.info(f"Deleted user with id {user_id}")
            return {"deleted user": db_user}
        except Exception as e:
            self.db.rollback()
            error_logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise DatabaseQueryException(str(e))

    def export_users_info_excel(self):
        try:
            users = self.db.query(User).all()

            # Prepare data for DataFrame
            user_info = []
            for user in users:
                user_info.append({
                    'Имя': user.name,
                    'Фамилия': user.surname,
                    'Логин': user.login,
                    'Доступный Баланс': user.available_balance,
                    'Потраченно': user.spent_money,
                })

            # Create DataFrame
            df = pd.DataFrame(user_info)

            # Prepare Excel output in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Информация о пользователях')

            output.seek(0)
            success_logger.info("Exported users info to Excel successfully")

            return output
        except Exception as e:
            error_logger.error(f"Error exporting users info to Excel: {str(e)}")
            raise FileExportFailedException(str(e))


