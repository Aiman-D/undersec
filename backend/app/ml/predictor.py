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

# Add 'threshold' as a parameter!
def predict_query_risk(feature_vector: list, threshold: float = -0.05) -> dict:
    if not model:
        return {"score": 0.0, "status": "ERROR", "level": "MODEL_MISSING"}
        
    X = np.array(feature_vector).reshape(1, -1)
    score = float(model.decision_function(X)[0])
    
    # Use the dynamic threshold here
    if score >= 0.05:
        level = "SAFE"
        status = "ALLOWED"
    elif score >= 0.0:
        level = "LOW RISK"
        status = "ALLOWED"
    elif score >= threshold: # <--- DYNAMIC VARIABLE HERE
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