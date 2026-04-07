import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
import os

FEATURE_COLS = [
    "qt_score", "schema_change", "has_multi_statement",
    "has_comment", "has_union", "rows_affected_log",
    "time_of_day", "user_frequency", "q_len",
    "complexity", "table_len"
]

def train_isolation_forest():
    print("Loading dataset...")
    
    if not os.path.exists("dataset.csv"):
        print("Error: dataset.csv not found. Run generate_dataset.py first.")
        return
        
    df = pd.read_csv("dataset.csv")
    
    # Train ONLY on normal queries (is_anomalous == 0) to establish a safe baseline
    normal_data = df[df["is_anomalous"] == 0][FEATURE_COLS]
    
    print(f"Training Isolation Forest on {len(normal_data)} normal queries...")
    
    # contamination defines the expected proportion of outliers.
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    model.fit(normal_data)
    
    joblib.dump(model, "isolation_forest.pkl")
    print("Model successfully saved to isolation_forest.pkl")

if __name__ == "__main__":
    train_isolation_forest()