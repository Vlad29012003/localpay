from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from db.database import Base
from schemas.user import RegionEnum, RoleEnum


class User(Base):
    __tablename__ = 'localpay_users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    surname = Column(String(100), nullable=True)
    login = Column(String(200), unique=True, nullable=True, index=True)
    hashed_password = Column(String(200), nullable=True)
    date_reg = Column(DateTime, default=datetime.utcnow)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)  # Новое поле роли
    access_to_payments = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    available_balance = Column(BigInteger, default=0)
    spent_money = Column(BigInteger, default=0)
    region = Column(Enum(RegionEnum), default=RegionEnum.CHUY, nullable=False)
    refill = Column(BigInteger, default=0)
    write_off = Column(BigInteger, default=0)
    comment = Column(Text, nullable=True)

    planup_id = Column(Integer, nullable=True)

    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    payments = relationship('Payment', back_populates='user', cascade='all, delete-orphan')
    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
