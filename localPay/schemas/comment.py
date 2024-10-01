from typing import Optional

from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    user_id: int
    text: Optional[str] = None
    payment_type: Optional[str] = None
    old_available_balance: int = 0
    old_spent_money: int = 0
    add_to_available_balance: int = 0
    add_to_spent_money: int = 0
    new_available_balance: int = 0
    new_spent_money: int = 0
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    user_id: Optional[int] = 0
    text: Optional[str] = None
    type_pay: Optional[str] = None
    old_available_balance: Optional[int] = 0
    old_spent_balance: Optional[int] = 0
    add_to_available_balance: Optional[int] = 0
    add_to_spent_balance: Optional[int] = 0
    new_available_balance: Optional[int] = 0
    new_spent_balance: Optional[int] = 0


class Comment(CommentBase):
    id: int

    class Config:
        from_attributes = True
