import re
from urllib.parse import urlparse
import math
from collections import Counter
import numpy as np
import os
import joblib

# Resolve path to the model saved in the backend root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "xgboost_phishing.pkl")

try:
    model = joblib.load(MODEL_PATH)
except (FileNotFoundError, Exception):
    model = None
import ipaddress

def is_ip_host(host_str: str) -> bool:
    if not host_str:
        return False
    h = host_str.strip("[]")
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        return bool(re.fullmatch(r'\d{1,3}(\.\d{1,3}){3}', h))

def extract_features(url: str):
    """
    Extracts 7 heuristic features from a target URL for XGBoost inference:
    1. len_url: Total URL length
    2. len_host: Hostname length
    3. count_digits: Total digits count in URL
    4. subdomains: Subdomain depth count
    5. has_ip: Boolean indicator (1 or 0) for IP address host
    6. non_alnum: Ratio of non-alphanumeric characters
    7. path_entropy: Shannon entropy of path and parameters
    """
    s = url if url.startswith(("http://", "https://")) else "http://" + url
    parsed = urlparse(s)
    host = parsed.hostname or ""
    path = (parsed.path or "") + ("?" + parsed.query if parsed.query else "")
    
    if path == "/":
        path = ""
    
    normalized_host = host.lower()
    if normalized_host.startswith('www.'):
        normalized_host = normalized_host[4:] 
    
    base_url_string = normalized_host + path 

    len_url = len(base_url_string) 
    len_host = len(normalized_host) 
    count_digits = sum(c.isdigit() for c in base_url_string) 
    subdomains = max(0, normalized_host.count('.') - 1)
    
    cnt = Counter(path)
    L = len(path) if len(path) else 1
    ent = -sum((c/L) * (math.log2(c/L)) for c in cnt.values()) if L > 0 else 0.0
    
    non_alnum = sum(1 for c in base_url_string if not c.isalnum()) / max(1, len(base_url_string))
    has_ip = is_ip_host(host)

    return [len_url, len_host, count_digits, subdomains, int(has_ip), non_alnum, ent]

def heuristic_score(url: str):
    s = url if url.startswith(("http://","https://")) else "http://" + url
    parsed = urlparse(s)
    host = parsed.hostname or ""
    path = (parsed.path or "") + ("?" + parsed.query if parsed.query else "")
    len_url = len(url); len_host = len(host); count_digits = sum(c.isdigit() for c in url)
    subdomains = max(0, host.count('.') - 1); cnt = Counter(path); L = len(path) if len(path) else 1
    ent = -sum((c/L) * (math.log2(c/L)) for c in cnt.values()) if L > 0 else 0.0
    non_alnum = sum(1 for c in url if not c.isalnum()) / max(1, len(url))
    has_ip = is_ip_host(host); score = 0; reasons = []
    
    if has_ip: score += 3; reasons.append("IP address used in domain")
    if len_url > 75: score += 2; reasons.append(f"URL length {len_url} > 75")
    if subdomains > 1: score += 2; reasons.append(f"{subdomains} subdomains")
    if '@' in url: score += 3; reasons.append("Contains '@' character")
    if '-' in url: reasons.append("Contains dash '-' in URL")
    if count_digits > 4: reasons.append(f"{count_digits} digits in URL")
    if non_alnum > 0.25: reasons.append("High non-alphanumeric character ratio")
    if ent > 3.5: reasons.append("High path entropy")
    
    risk_percentage = min((score / 8.0) * 100, 99.0)
    return risk_percentage, reasons

def predict_phishing_risk(url: str) -> dict:
    features = extract_features(url)
    h_score, h_reasons = heuristic_score(url)
    
    if model:
        try:
            X = np.array(features).reshape(1, -1)
            probs = model.predict_proba(X)[0]
            # Prob of class 1 is phishing risk
            risk_score = float(probs[1]) * 100
        except Exception as e:
            print(f"XGBoost Prediction Error: {e}")
            risk_score = h_score
    else:
        risk_score = h_score
        
    status = "BLOCKED" if risk_score > 60 else "FLAGGED" if risk_score > 30 else "ALLOWED"
    level = "HIGH RISK" if risk_score > 60 else "MEDIUM RISK" if risk_score > 30 else "SAFE"
    
    if status == "ALLOWED":
        reasons = ["Legitimate domain syntax verified by XGBoost 7-feature model."]
    else:
        reasons = h_reasons if h_reasons else [f"XGBoost anomaly probability flagged {round(risk_score, 1)}% risk."]
        
    return {
        "score": round(risk_score, 2),
        "level": level,
        "status": status,
        "reasons": reasons,
        "features": {
            "len_url": features[0],
            "len_host": features[1],
            "count_digits": features[2],
            "subdomains": features[3],
            "has_ip": bool(features[4]),
            "non_alnum": round(float(features[5]), 3),
            "path_entropy": round(float(features[6]), 3)
        }
    }
