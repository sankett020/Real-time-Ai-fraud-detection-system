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
import json
from app.ml.train import train_model

@router.get("/model/info")
def get_model_info():
    try:
        with open("artifacts/metrics.json", "r") as f:
            metrics = json.load(f)
        return metrics
    except:
        return {"error": "Model not trained yet."}

@router.post("/model/train")
def trigger_train():
    metrics = train_model()
    return metrics

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    res = []
    for alert in alerts:
        tx = db.query(Transaction).filter(Transaction.id == alert.transaction_id).first()
        res.append({
            "id": alert.id,
            "status": alert.status,
            "notes": alert.notes,
            "created_at": alert.created_at,
            "transaction": tx
        })
    return res

@router.patch("/alerts/{alert_id}")
def update_alert(alert_id: int, update: AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if update.status:
        alert.status = update.status
    if update.notes:
        alert.notes = update.notes
    db.commit()
    db.refresh(alert)
    return alert
