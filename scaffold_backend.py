import os

files = {
    "backend/app/core/config.py": """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinel AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./sentinel.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
""",
    "backend/app/db/session.py": """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "backend/app/db/base_class.py": """
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
""",
    "backend/app/models/transaction.py": """
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
""",
    "backend/app/schemas/transaction.py": """
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
""",
    "backend/app/ml/predict.py": """
import random
import os
import joblib

MODEL_PATH = "artifacts/model.pkl"

def get_risk_score(data: dict) -> float:
    # Dummy ML model for now
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            # In a real scenario, format data for prediction
            # score = model.predict_proba(formatted_data)[0][1]
            score = random.random()
        except:
            score = random.random()
    else:
        # Rule based fallback
        score = min(data.get("amount", 0) / 10000.0, 1.0)
    return score

def categorize_risk(score: float) -> str:
    if score < 0.35:
        return "Low Risk"
    elif score < 0.65:
        return "Review"
    else:
        return "High Risk"
""",
    "backend/app/api/endpoints.py": """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.transaction import Transaction, Alert
from app.schemas.transaction import TransactionCreate, TransactionResponse, AlertUpdate
from app.ml.predict import get_risk_score, categorize_risk
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/transactions/analyze", response_model=TransactionResponse)
def analyze_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    tx_data = tx.model_dump()
    score = get_risk_score(tx_data)
    category = categorize_risk(score)
    
    db_tx = Transaction(**tx_data, risk_score=score, risk_category=category)
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    
    if category in ["Review", "High Risk"]:
        alert = Alert(transaction_id=db_tx.id)
        db.add(alert)
        db.commit()
        
    return db_tx

@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/dashboard/summary")
def get_summary(db: Session = Depends(get_db)):
    total = db.query(Transaction).count()
    high_risk = db.query(Transaction).filter(Transaction.risk_category == "High Risk").count()
    review = db.query(Transaction).filter(Transaction.risk_category == "Review").count()
    
    return {
        "total_transactions": total,
        "high_risk": high_risk,
        "review": review,
        "flagged_percentage": ((high_risk + review) / total * 100) if total > 0 else 0
    }
""",
    "backend/app/main.py": """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from app.db.session import engine
from app.db.base_class import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sentinel AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
"""
}

for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content.strip())

print("Backend files generated successfully!")
