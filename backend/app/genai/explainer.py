import requests
import os

# Default to local Ollama. You can change the model to 'mistral' if preferred.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("LLM_MODEL", "llama3") 

def generate_explanation(query: str, score: float, user: str, features: dict) -> str:
    prompt = f"""Explain why this database query is suspicious. 
    Query: {query}
    Score: {score}
    User: {user}
    Features: {features}
    
    Give a concise security explanation in 1 to 2 sentences max."""

    try:
        # 1. Try Local Ollama Model
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
            
    except requests.exceptions.RequestException:
        print("Warning: Ollama not reachable. Falling back to rule-based explanation.")

    # 2. Smart Fallback (If Ollama is down or not installed yet)
    explanation = "Suspicious query detected. "
    if features.get("qt_score", 0) >= 8:
        explanation += "Contains highly destructive commands (DROP/ALTER). "
    elif features.get("qt_score", 0) >= 5:
        explanation += "Contains bulk deletion commands. "
        
    if features.get("has_union", 0) > 0:
        explanation += "Detected UNION keyword, indicating potential data exfiltration (SQLi). "
    if features.get("schema_change", 0) > 0:
        explanation += "Attempted unauthorized database schema modification. "
    if features.get("has_multi_statement", 0) > 0:
        explanation += "Detected piggybacked multiple statements (;). "

    if explanation == "Suspicious query detected. ":
        explanation += "Query structure heavily deviates from normal user baselines."

    return explanation.strip()