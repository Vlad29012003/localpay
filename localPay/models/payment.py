from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from db.database import Base
from models import comment, user


class Payment(Base):
    __tablename__ = 'localpay_payments'

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(100), nullable=True)
    payment_date = Column(DateTime, nullable=True)
    payment_accept = Column(DateTime, nullable=True)
    ls_abon = Column(String(100), nullable=True)
    money = Column(Float, nullable=True)
    payment_status = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey('localpay_users.id'))
    annulment = Column(Boolean, default=False)
    document_number = Column(String(100), nullable=True)
    comment = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='payments')
