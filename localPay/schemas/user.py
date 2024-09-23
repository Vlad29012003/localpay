from typing import Optional

import enum
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class RegionEnum(str, Enum):
    CHUY = 'Чуйская'
    ISSYK_KUL = 'Иссык-кульская'
    NARYN = 'Нарынская'
    JALAL_ABAD = 'Джалал-Абадская'
    BATKEN = 'Баткенская'
    OSH = 'Ошская'
    TALAS = 'Таласская'


class RoleEnum(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
    SUPERVISOR = 'supervisor'



class UserBase(BaseModel):
    name: str
    surname: str
    login: str
    role: RoleEnum = RoleEnum.USER
    access_to_payments: bool = False
    is_active: bool = False
    available_balance: int = 0
    spent_money: int = 0
    region: RegionEnum = RegionEnum.CHUY
    refill: int = 0
    write_off: int = 0
    comment: Optional[str] = None
    planup_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., max_length=200)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    login: Optional[str] = None
    hashed_password: Optional[str] = None
    role: Optional[RoleEnum] = RoleEnum.USER
    access_to_payments: Optional[bool] = False
    is_active: Optional[bool] = False
    available_balance: Optional[int] = 0
    spent_money: Optional[int] = 0
    region: Optional[RegionEnum] = RegionEnum.CHUY
    refill: Optional[int] = 0
    write_off: Optional[int] = 0
    comment: Optional[str] = None
    planup_id: Optional[int] = None


class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True



