import pandas as pd
import numpy as np
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
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(backend_dir, "dataset.csv")
    model_path = os.path.join(backend_dir, "isolation_forest.pkl")
    
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} not found. Run generate_dataset.py first.")
        return
        
    df = pd.read_csv(dataset_path)
    
    # Train ONLY on normal queries (is_anomalous == 0) to establish a safe baseline
    normal_data = df[df["is_anomalous"] == 0][FEATURE_COLS].values.astype(np.float64)
    
    print(f"Training Isolation Forest on {len(normal_data)} normal queries...")
    
    # Contamination parameter for outlier sensitivity
    model = IsolationForest(
        n_estimators=150,
        contamination=0.03,
        random_state=42,
        bootstrap=False
    )
    model.fit(normal_data)
    
    joblib.dump(model, model_path)
    print(f"Model successfully saved to: {model_path}")

    # Quick sanity check
    safe_test = np.array([[0, 0, 0, 0, 0, 1.2, 14.0, 1.0, 48.0, 0.0, 8.0]])
    bad_test = np.array([[10, 5, 3, 3, 3, 10.5, 3.0, 1.0, 250.0, 8.0, 20.0]])
    print("Sanity Check Safe Score:", round(model.decision_function(safe_test)[0], 4))
    print("Sanity Check Bad Score:", round(model.decision_function(bad_test)[0], 4))

if __name__ == "__main__":
    train_isolation_forest()