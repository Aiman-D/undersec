import requests
import time
import random

BASE_URL = "http://localhost:8000/api"

NORMAL_QUERIES = [
    "SELECT * FROM users WHERE status = 'active';",
    "SELECT id, username FROM users WHERE last_login > '2023-01-01';",
    "UPDATE users SET last_login = NOW() WHERE id = 123;",
    "INSERT INTO logs (event, user_id) VALUES ('login', 456);",
    "SELECT COUNT(*) FROM products WHERE stock > 0;",
    "SELECT name, price FROM products ORDER BY price DESC LIMIT 10;",
    "UPDATE inventory SET count = count - 1 WHERE product_id = 999;",
    "SELECT * FROM orders WHERE user_id = 42 AND status = 'shipped';",
    "SELECT SUM(amount) FROM transactions WHERE date = CURRENT_DATE;"
]

MALICIOUS_QUERIES = [
    "SELECT * FROM users WHERE username = 'admin' OR 1=1 --",
    "DROP TABLE users;",
    "SELECT * FROM accounts WHERE id = 1 UNION SELECT username, password FROM users;",
    "TRUNCATE TABLE logs;",
    "UPDATE users SET role = 'admin' WHERE id = 42 OR 1=1;",
    "SELECT * FROM products WHERE name = '' OR '' = '';"
]

SUSPICIOUS_QUERIES = [
    "SELECT * FROM users; SELECT * FROM products;", # multiple statements
    "SELECT * FROM users WHERE status = 'active' OR role = 'admin' OR id > 0;" # lots of ORs
]

PHISHING_URLS = [
    "http://secure-login-apple-update.com/verify",
    "https://paypal.security-check-2023.net/login",
    "http://192.168.1.55/admin/login.php",
    "http://netflix.account-billing-update.info/"
]

SAFE_URLS = [
    "https://www.google.com",
    "https://github.com/Aiman-D",
    "https://reactjs.org/docs/getting-started.html"
]

def send_sql_query(query, user="demo_user"):
    try:
        res = requests.post(f"{BASE_URL}/query", json={"query": query, "user": user})
        print(f"[SQL] {res.status_code} - {res.json().get('status')} - {query[:50]}...")
    except Exception as e:
        print(f"[SQL] Failed to send query: {e}")

def send_phishing_check(url):
    try:
        res = requests.post(f"{BASE_URL}/phishing/analyze", json={"url": url})
        print(f"[PHISH] {res.status_code} - {res.json().get('status')} - {url}")
    except Exception as e:
        print(f"[PHISH] Failed to check URL: {e}")

if __name__ == "__main__":
    print("Starting Live Demo Traffic Generator...")
    print("Sending traffic to", BASE_URL)
    
    while True:
        # Decide what to do
        action = random.choices(
            ['normal_sql', 'malicious_sql', 'suspicious_sql', 'phish_check', 'safe_check'],
            weights=[70, 5, 10, 5, 10] # 70% normal traffic, 5% malicious, etc.
        )[0]
        
        if action == 'normal_sql':
            send_sql_query(random.choice(NORMAL_QUERIES))
        elif action == 'malicious_sql':
            send_sql_query(random.choice(MALICIOUS_QUERIES), user="hacker_01")
        elif action == 'suspicious_sql':
            send_sql_query(random.choice(SUSPICIOUS_QUERIES), user="unknown_user")
        elif action == 'phish_check':
            send_phishing_check(random.choice(PHISHING_URLS))
        elif action == 'safe_check':
            send_phishing_check(random.choice(SAFE_URLS))
            
        # Random sleep between 0.5 and 2 seconds
        time.sleep(random.uniform(0.5, 2.0))
