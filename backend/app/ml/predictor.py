import joblib
import numpy as np
import os

# Resolve path to the model saved in the backend root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "isolation_forest.pkl")

try:
    model = joblib.load(MODEL_PATH)
except FileNotFoundError:
    model = None
    print(f"Warning: Model not found at {MODEL_PATH}. Run train_model.py first.")

def predict_query_risk(feature_vector: list) -> dict:
    """
    Scores the query vector. Returns the raw score and the mapped risk level.
    """
    if not model:
        return {"score": 0.0, "status": "ERROR", "level": "MODEL_MISSING"}
        
    X = np.array(feature_vector).reshape(1, -1)
    
    # decision_function returns > 0 for inliers (safe), < 0 for outliers (anomalies)
    score = float(model.decision_function(X)[0])
    
    # TIGHTER THRESHOLDS: 
    # Anything below 0.0 is mathematically an anomaly in Isolation Forest.
    if score >= 0.05:
        level = "SAFE"
        status = "ALLOWED"
    elif score >= 0.0:
        level = "LOW RISK"
        status = "ALLOWED"
    elif score >= -0.05:
        level = "MEDIUM RISK"
        status = "FLAGGED" 
    else:
        level = "HIGH RISK"
        status = "BLOCKED" 

    return {
        "score": round(score, 4),
        "level": level,
        "status": status
    }