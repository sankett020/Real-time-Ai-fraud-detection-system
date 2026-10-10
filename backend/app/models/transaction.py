from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from app.db.base_class import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    merchant_category = Column(String, index=True)
    transaction_type = Column(String)
    distance_from_home = Column(Float)
    recent_transactions = Column(Integer)
    new_device = Column(Boolean)
    
    risk_score = Column(Float)
    risk_category = Column(String, index=True)
    is_demo = Column(Boolean, default=False)
    
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    status = Column(String, default="Open") # Open, Investigating, Resolved, False Positive
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)