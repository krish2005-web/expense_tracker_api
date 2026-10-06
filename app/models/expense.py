from sqlalchemy import Column,Integer,String,Float,Text,ForeignKey,DateTime,Date
from app.database import Base
from datetime import datetime
from app.models.user import User
class Expense(Base):
    __tablename__="expenses"
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(50),nullable=False)
    amount=Column(Float,nullable=False)
    category=Column(String(50),nullable=False)
    description=Column(Text,nullable=True)
    expense_date=Column(Date,nullable=False)
    created_at=Column(DateTime,nullable=False,default=datetime.utcnow())
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    receipt_path = Column(String(255), nullable=True)


