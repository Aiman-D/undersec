import pandas as pd
import numpy as np
import random
import os
import sys

# Ensure app modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.feature_extractor import extract_features, features_to_vector

def generate_synthetic_data(num_samples=1000):
    data = []
    
    safe_queries = [
        "SELECT * FROM users WHERE id = 1",
        "SELECT name, email FROM customers",
        "INSERT INTO logs (event) VALUES ('login')",
        "UPDATE settings SET theme = 'dark' WHERE user_id = 5",
        "SELECT count(*) FROM orders JOIN users ON users.id = orders.user_id"
    ]
    
    malicious_queries = [
        "DROP TABLE users;",
        "DELETE FROM customers;", # Missing WHERE
        "SELECT * FROM users WHERE id = 1 OR 1=1; --", # SQLi
        "SELECT * FROM users UNION SELECT password, username FROM admin", # Union SQLi
        "ALTER TABLE payments DROP COLUMN amount"
    ]
    
    for _ in range(num_samples):
        is_malicious = random.random() < 0.1
        
        if is_malicious:
            q_text = random.choice(malicious_queries)
            rows = random.randint(1000, 50000) 
            hour = random.choice([2, 3, 4]) # Often off-hours
        else:
            q_text = random.choice(safe_queries)
            rows = random.randint(1, 10)
            hour = random.randint(8, 18) # Normal business hours
            
        features_dict = extract_features(q_text, user="user1", time_of_day=hour, rows_affected=rows)
        vector = features_to_vector(features_dict)
        
        row = vector + [1 if is_malicious else 0, q_text]
        data.append(row)
        
    columns = [
        "qt_score", "schema_change", "has_multi_statement", 
        "has_comment", "has_union", "rows_affected_log", 
        "time_of_day", "user_frequency", "q_len", 
        "complexity", "table_len", "is_anomalous", "query_text"
    ]
    
    df = pd.DataFrame(data, columns=columns)
    df.to_csv("dataset.csv", index=False)
    print(f"Generated dataset.csv with {num_samples} samples.")

if __name__ == "__main__":
    generate_synthetic_data()