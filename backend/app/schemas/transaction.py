from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    amount: float
    merchant_category: str
    transaction_type: str
    distance_from_home: float
    recent_transactions: int
    new_device: bool

class TransactionCreate(TransactionBase):
    is_demo: bool = False

class TransactionResponse(TransactionBase):
    id: int
    timestamp: datetime
    risk_score: float
    risk_category: str
    is_demo: bool
    
    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None