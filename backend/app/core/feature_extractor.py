import re
import numpy as np

def extract_features(query_text: str, user: str, time_of_day: int = 12, rows_affected: int = 1) -> dict:
    """Extracts 11 ML features from an SQL query with weighted threat signals."""
    q_upper = query_text.upper()
    
    # 1. Query Type Score (Heavy scaling for separation)
    if "DROP" in q_upper: qt_score = 10
    elif "ALTER" in q_upper: qt_score = 8
    elif "DELETE" in q_upper or "TRUNCATE" in q_upper: qt_score = 5
    elif "UPDATE" in q_upper: qt_score = 2
    elif "INSERT" in q_upper: qt_score = 1
    else: qt_score = 0  # SELECT
        
    # 2. Schema Change (High penalty)
    schema_change = 5 if any(kw in q_upper for kw in ["DROP", "ALTER", "CREATE"]) else 0
    
    # 3. Multi-statement (Classic SQLi / Piggybacking)
    stripped_q = query_text.strip().rstrip(";")
    has_multi_statement = 3 if ";" in stripped_q else 0
    
    # 4. Comments (Often used in SQLi auth bypass)
    has_comment = 3 if "--" in query_text or "/*" in query_text else 0
    
    # 5. Union (Classic SQLi exfiltration)
    has_union = 3 if "UNION" in q_upper else 0
    
    # 6. Rows Affected (Log scaled to handle massive variance smoothly)
    rows_affected_log = np.log1p(rows_affected)
    
    # 7. Time of day (Normalizing to 0-24)
    time_of_day_val = float(time_of_day)
    
    # 8. User frequency (mocked baseline)
    user_frequency = 1.0 
    
    # 9. Query Length
    q_len = len(query_text)
    
    # 10. Complexity Score (Counts of JOIN, AND, OR)
    complexity = q_upper.count("JOIN") + q_upper.count("AND") + q_upper.count("OR")
    
    # 11. Table Name Length (Heuristic for obfuscated automated queries)
    table_match = re.search(r'(?:FROM|UPDATE|JOIN|INTO)\s+([a-zA-Z0-9_]+)', q_upper)
    table_len = len(table_match.group(1)) if table_match else 0

    return {
        "qt_score": qt_score,
        "schema_change": schema_change,
        "has_multi_statement": has_multi_statement,
        "has_comment": has_comment,
        "has_union": has_union,
        "rows_affected_log": rows_affected_log,
        "time_of_day": time_of_day_val,
        "user_frequency": user_frequency,
        "q_len": q_len,
        "complexity": complexity,
        "table_len": table_len
    }

def features_to_vector(features: dict) -> list:
    """Converts the feature dictionary into an ordered 11-D array for the model."""
    return [
        features["qt_score"],
        features["schema_change"],
        features["has_multi_statement"],
        features["has_comment"],
        features["has_union"],
        features["rows_affected_log"],
        features["time_of_day"],
        features["user_frequency"],
        features["q_len"],
        features["complexity"],
        features["table_len"]
    ]