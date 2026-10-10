
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json
import os

MODEL_PATH = "artifacts/model.pkl"
METRICS_PATH = "artifacts/metrics.json"

def train_model(dataset_path: str = None):
    # If no dataset_path provided or file not found, use a demo dataset generator
    if dataset_path is None or not os.path.exists(dataset_path):
        print("Using demo dataset...")
        np.random.seed(42)
        n_samples = 1000
        
        # Synthetic features: amount, distance_from_home, recent_transactions, new_device
        # Target: is_fraud (0 or 1)
        
        amount = np.random.exponential(scale=50, size=n_samples)
        distance = np.random.exponential(scale=10, size=n_samples)
        recent = np.random.poisson(lam=2, size=n_samples)
        new_device = np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1])
        
        # Simple logic to generate fraud
        prob_fraud = (amount / 1000) + (distance / 100) + (new_device * 0.2)
        is_fraud = (prob_fraud + np.random.normal(0, 0.1, n_samples) > 0.4).astype(int)
        
        df = pd.DataFrame({
            'amount': amount,
            'distance_from_home': distance,
            'recent_transactions': recent,
            'new_device': new_device,
            'is_fraud': is_fraud
        })
    else:
        # Load from CSV (e.g. European credit card dataset, simplified)
        df = pd.read_csv(dataset_path)

    X = df[['amount', 'distance_from_home', 'recent_transactions', 'new_device']]
    y = df['is_fraud']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    clf = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced')
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    
    metrics = {
        "accuracy": acc,
        "confusion_matrix": cm,
        "n_samples": len(df),
        "is_demo": (dataset_path is None or not os.path.exists(dataset_path))
    }
    
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f)
        
    return metrics

if __name__ == "__main__":
    train_model()
