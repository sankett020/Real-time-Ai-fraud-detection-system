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