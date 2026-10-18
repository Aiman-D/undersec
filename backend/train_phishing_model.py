import os
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from app.ml.phishing_model import extract_features

LEGITIMATE_URLS = [
    "https://www.google.com",
    "https://panasonic.com",
    "https://na.panasonic.com/us/automotive-solutions",
    "https://holdings.panasonic/global",
    "https://connect.panasonic.com/jp-ja/products-services/touch-displays",
    "https://github.com/Aiman-D/undersec",
    "https://github.com",
    "https://microsoft.com/en-us",
    "https://apple.com/macbook-pro",
    "https://amazon.com/dp/B08N5WRWNW",
    "https://lexus.com/models/RX",
    "https://toyota.com/crown",
    "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
    "https://react.dev/learn",
    "https://en.wikipedia.org/wiki/Deep_packet_inspection",
    "https://postgresql.org/docs/current/protocol.html",
    "https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html",
    "https://xgboost.readthedocs.io/en/stable/",
    "https://ultralytics.com/yolov8",
    "https://opencv.org/releases/",
    "https://docs.python.org/3/library/asyncio.html",
    "https://nytimes.com",
    "https://bbc.com/news",
    "https://stackoverflow.com/questions/21356547",
    "https://developer.mozilla.org/en-US/docs/Web/API",
    "https://cloudflare.com/products/zero-trust",
    "https://netflix.com/browse",
    "https://spotify.com/us/premium",
    "https://linkedin.com/in/security-engineer",
    "https://kaggle.com/datasets"
]

PHISHING_URLS = [
    "http://secure-login-apple-update.com/verify?account=91283",
    "https://paypal.security-check-2023.net/login/auth.php?session=ax992",
    "http://192.168.1.55/admin/login.php",
    "http://10.0.0.12/wp-login.php?redirect_to=admin",
    "http://netflix.account-billing-update.info/sign-in/verification",
    "http://panasonic-showroom-kiosk-auth.cfd/verify-admin-session",
    "http://lexus-configurator-asset-bypass.tk/malware.exe",
    "http://chase.online-banking-alert-update.secure-auth892.xyz/index.html",
    "http://wellsfargo.account-locked-verify.co.vu/auth/signin?token=92847",
    "http://microsoft.office365-password-reset.live-security-update.club/login",
    "http://bankofamerica.signon-security.top/customer/verify.php",
    "http://dhl-package-reschedule-fee.download-form.site/pay.php",
    "http://google-drive-shared-doc-view.account-sync.pw/auth",
    "http://198.51.100.44/sec/panasonic/kiosk_override.php",
    "http://usps-tracking-failed-delivery-fee.redirection-portal.vip/confirm",
    "http://binance.anti-phishing-code-reset.security-portal.cc/2fa",
    "http://coinbase.wallet-recovery-phrase.support-desk.top/seed",
    "http://instagram.copyright-infringement-appeal.help-center.biz/notice",
    "http://adobe-pdf-invoice-viewer.dropbox-shared-download.click/invoice",
    "http://amazon.prime-renewal-billing-failure.account-check.site/portal"
]

def generate_url_dataset():
    data = []
    
    # Base URLs
    for url in LEGITIMATE_URLS:
        features = extract_features(url)
        data.append(features + [0])
        
    for url in PHISHING_URLS:
        features = extract_features(url)
        data.append(features + [1])
        
    # Synthetically expand with realistic permutations
    for i in range(150):
        # Normal permutations: short domains, standard paths
        dom = np.random.choice(["company", "service", "app", "cloud", "portal", "store", "automotive"])
        tld = np.random.choice([".com", ".org", ".net", ".io", ".tech", ".co"])
        path = np.random.choice(["", "/about", "/pricing", "/products/item", "/dashboard", "/docs/guide", "/blog/post-1"])
        url = f"https://www.{dom}{i}{tld}{path}"
        data.append(extract_features(url) + [0])
        
    for i in range(150):
        # Phishing permutations: IP addresses, multiple hyphens, deep subdomains, suspicious tlds, high path entropy
        is_ip = np.random.random() < 0.3
        if is_ip:
            ip = f"{np.random.randint(1,255)}.{np.random.randint(0,255)}.{np.random.randint(0,255)}.{np.random.randint(1,254)}"
            url = f"http://{ip}/login/auth-{i}?token={hex(np.random.randint(100000, 999999))}"
        else:
            subs = ".".join([f"sub{j}" for j in range(np.random.randint(2, 5))])
            kw = np.random.choice(["secure-login", "account-verify", "billing-update", "credential-check", "system-auth"])
            tld = np.random.choice([".xyz", ".top", ".info", ".cfd", ".club", ".click", ".pw", ".site"])
            random_hex = "".join([f"{np.random.randint(0,16):x}" for _ in range(16)])
            url = f"http://{subs}.{kw}-{i}{tld}/path/{random_hex}/confirm.php?user=victim_{i}"
        data.append(extract_features(url) + [1])
        
    cols = ["len_url", "len_host", "count_digits", "subdomains", "has_ip", "non_alnum", "path_entropy", "is_phishing"]
    return pd.DataFrame(data, columns=cols)

def train_phishing_xgboost():
    print("Generating URL feature dataset for XGBoost training...")
    df = generate_url_dataset()
    
    feature_cols = ["len_url", "len_host", "count_digits", "subdomains", "has_ip", "non_alnum", "path_entropy"]
    X = df[feature_cols]
    y = df["is_phishing"]
    
    print(f"Training XGBoost on {len(df)} URL samples with 7 heuristic features...")
    model = XGBClassifier(
        n_estimators=120,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X, y)
    
    # Save model
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(backend_dir, "xgboost_phishing.pkl")
    joblib.dump(model, model_path)
    print(f"XGBoost Phishing model successfully trained and saved to: {model_path}")
    
    # Test on test cases
    test_urls = [
        ("https://panasonic.com/global", 0),
        ("http://192.168.1.100/panasonic/login.php", 1),
        ("http://secure-login.panasonic-update.xyz/verify", 1),
        ("https://github.com/Aiman-D/undersec", 0),
    ]
    print("\n--- Model Validation Tests ---")
    for u, expected in test_urls:
        feats = np.array(extract_features(u)).reshape(1, -1)
        prob = model.predict_proba(feats)[0][1]
        pred = int(prob > 0.5)
        status = "PASS" if pred == expected else "FAIL"
        print(f"[{status}] URL: {u} -> P(phish)={prob:.4f} (Expected: {expected})")

if __name__ == "__main__":
    train_phishing_xgboost()
