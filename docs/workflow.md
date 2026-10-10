# Sentinel AI Workflow

Dataset or demo input -> Data validation -> Preprocessing -> Feature engineering -> Model inference -> Risk scoring -> Explanation -> Database persistence -> Dashboard and alert investigation.

## Process Details

1. **Dataset or demo input**: The system either loads a real CSV dataset specified in configuration or generates deterministic synthetic data if none is provided.
2. **Data validation**: Ensures required columns are present and data types are correct.
3. **Preprocessing**: Handles missing values and scales features like transaction amount and distance from home.
4. **Feature engineering**: Extracts relevant signals such as recent transaction frequency and new device flags.
5. **Model inference**: Uses a trained Random Forest model (scikit-learn) to predict the probability of fraud based on engineered features.
6. **Risk scoring**: Converts the raw prediction probability into a categorized risk level (Low Risk, Review, High Risk) using configurable thresholds.
7. **Explanation**: Associates the main contributing factors (e.g., high distance or new device) with the risk score to provide transparent insights for the analyst.
8. **Database persistence**: Saves the transaction details, risk score, and category to the SQLite database via SQLAlchemy. High-risk transactions trigger an alert entry.
9. **Dashboard and alert investigation**: Analysts view aggregated metrics on the dashboard, explore historical transactions, and manage active alerts in the Alerts Center, changing statuses and leaving investigation notes.
