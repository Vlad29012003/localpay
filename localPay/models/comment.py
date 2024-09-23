from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.database import Base
from models import payment, user


class Comment(Base):
    __tablename__ = 'localpay_comments'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('localpay_users.id', ondelete="CASCADE"))
    text = Column(Text, nullable=True)
    payment_type = Column(String(30), nullable=True)

    old_available_balance = Column(BigInteger, default=0)
    old_spent_money = Column(BigInteger, default=0)

    add_to_available_balance = Column(BigInteger, default=0)
    add_to_spent_money = Column(BigInteger, default=0)

    new_available_balance = Column(BigInteger, default=0)
    new_spent_money = Column(BigInteger, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="comments")