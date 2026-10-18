import pandas as pd
import numpy as np
import random
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.feature_extractor import extract_features, features_to_vector

def generate_synthetic_data(num_samples=2000):
    data = []
    
    tables = ["users", "vehicles", "showroom_inventory", "telemetry_logs", "configurator_sessions", "orders", "devices", "analytics", "customers", "displays"]
    columns_list = ["id", "status", "created_at", "vin", "model_name", "price", "location", "battery_pct", "temp_c", "session_token"]
    users = ["admin", "showroom_app", "telemetry_agent", "pos_terminal", "inventory_service", "web_client", "staff_kiosk"]
    
    # Diverse legitimate queries
    safe_templates = [
        "SELECT id, model_name, price FROM vehicles WHERE status = 'available' LIMIT 10",
        "SELECT * FROM showroom_inventory WHERE location = 'Zone 1' AND status = 'active'",
        "SELECT count(*) FROM configurator_sessions WHERE created_at > '2026-04-01'",
        "SELECT id, battery_pct, temp_c FROM telemetry_logs WHERE vin = 'JTDKN3DU' ORDER BY id DESC LIMIT 1",
        "UPDATE devices SET status = 'online' WHERE id = 12",
        "INSERT INTO configurator_sessions (vin, user_id, status) VALUES ('JTDKN3', 42, 'configuring')",
        "SELECT u.id, u.name, o.price FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status = 'confirmed'",
        "SELECT * FROM displays WHERE status = 'HEALTHY'",
        "SELECT AVG(temp_c) FROM telemetry_logs GROUP BY location",
        "SELECT id, vin, status FROM vehicles ORDER BY price DESC LIMIT 20 OFFSET 10",
        "UPDATE showroom_inventory SET stock = stock - 1 WHERE id = 101",
        "INSERT INTO telemetry_logs (temp_c, battery_pct) VALUES (24.5, 98)",
        "SELECT name, location FROM displays WHERE ambient_lux > 400"
    ]
    
    # Malicious queries
    malicious_templates = [
        "DROP TABLE users;",
        "DROP TABLE vehicles;",
        "TRUNCATE TABLE telemetry_logs;",
        "SELECT * FROM users WHERE id = 1 OR 1=1; --",
        "SELECT * FROM users WHERE username = 'admin' /* SQLi */ OR 'a'='a'",
        "SELECT * FROM accounts WHERE id = 1 UNION SELECT password, username, email FROM admin_users",
        "SELECT * FROM orders UNION SELECT card_number, cvv, exp FROM credit_cards",
        "ALTER TABLE devices DROP COLUMN tamper_sensor;",
        "DELETE FROM showroom_inventory;", # Dangerous missing WHERE
        "SELECT * FROM vehicles; DROP TABLE orders; --",
        "UPDATE users SET role = 'superadmin' WHERE id = 1 OR 1=1"
    ]
    
    for _ in range(num_samples):
        is_malicious = random.random() < 0.12
        user = random.choice(users) if not is_malicious else random.choice(["sqli_bot", "attacker", "unknown_client"])
        
        if is_malicious:
            q_text = random.choice(malicious_templates)
            rows = random.randint(1000, 100000)
            hour = random.choice([1, 2, 3, 4, 23])
        else:
            q_text = random.choice(safe_templates)
            # Add minor variation
            if random.random() < 0.3:
                q_text += f" -- request_id={random.randint(100, 999)}"
            rows = random.randint(1, 25)
            hour = random.randint(8, 20)
            
        features_dict = extract_features(q_text, user=user, time_of_day=hour, rows_affected=rows)
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
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.csv")
    df.to_csv(output_path, index=False)
    print(f"Generated {output_path} with {num_samples} samples.")

if __name__ == "__main__":
    generate_synthetic_data()