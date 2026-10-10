# Sentinel AI — Real-Time Intelligent Fraud Detection System

Sentinel AI is an intelligent transaction-monitoring platform that estimates the probability of financial fraud by analyzing transaction characteristics and behavioral patterns.

## Features
- **Dashboard**: Real-time overview of transactions, risk levels, and alerts.
- **Transaction Analyzer**: Interactive form to score individual transactions using a machine-learning model.
- **Transaction Explorer**: Searchable and filterable history of analyzed transactions.
- **Alerts Center**: Dedicated interface to manage and investigate high-risk transactions.

## Tech Stack
- **Frontend**: React, Vite, Tailwind CSS, Recharts
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Machine Learning**: scikit-learn, joblib

## Setup Instructions

### Backend
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`

## Disclaimer
This is an academic prototype for educational purposes. It is not a certified financial fraud prevention system. Predictions do not prove criminal activity.
