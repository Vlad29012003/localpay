from typing import Optional

from datetime import datetime
from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    payment_number: str
    payment_date: datetime
    payment_accept: datetime
    ls_abon: str
    money: float
    payment_status: str
    user_id: int
    annulment: bool = False
    document_number: str
    comment: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_number: Optional[str] = None
    payment_date: Optional[datetime] = None
    payment_accept: Optional[datetime] = None
    ls_abon: Optional[str] = None
    money: Optional[float] = None
    payment_status: Optional[str] = None
    user_id: Optional[int] = None
    annulment: Optional[bool] = False
    document_number: Optional[str] = None
    comment: Optional[str] = None
    updated_at: Optional[datetime] = None


class Payment(PaymentBase):
    id: int

    class Config:
        from_attributes = True