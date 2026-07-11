import pytest
from app.core.feature_extractor import extract_features, features_to_vector

def test_extract_features_normal_select():
    query = "SELECT id, name FROM users WHERE status = 'active';"
    features = extract_features(query, "test_user")
    
    assert features["qt_score"] == 0
    assert features["schema_change"] == 0
    assert features["has_multi_statement"] == 0
    assert features["has_comment"] == 0
    assert features["has_union"] == 0
    assert features["q_len"] == len(query)

def test_extract_features_sql_injection():
    query = "SELECT * FROM users WHERE username = 'admin' /* SQLi payload */ OR 1=1 UNION SELECT password FROM users;"
    features = extract_features(query, "hacker")
    
    assert features["qt_score"] == 0
    assert features["has_comment"] == 3
    assert features["has_union"] == 3
    assert features["complexity"] > 0

def test_extract_features_schema_change():
    query = "DROP TABLE users;"
    features = extract_features(query, "bad_actor")
    
    assert features["qt_score"] == 10
    assert features["schema_change"] == 5

def test_extract_features_multi_statement():
    query = "SELECT * FROM products; DELETE FROM logs;"
    features = extract_features(query, "test_user")
    
    assert features["has_multi_statement"] == 3
    assert features["qt_score"] >= 5  # DELETE should set it to 5

def test_features_to_vector():
    features = {
        "qt_score": 10,
        "schema_change": 5,
        "has_multi_statement": 3,
        "has_comment": 0,
        "has_union": 0,
        "rows_affected_log": 2.5,
        "time_of_day": 12.0,
        "user_frequency": 1.0,
        "q_len": 50,
        "complexity": 2,
        "table_len": 5
    }
    
    vector = features_to_vector(features)
    assert len(vector) == 11
    assert vector[0] == 10
    assert vector[1] == 5
    assert vector[-1] == 5
