import os
import base64
import requests

def get_digicash_token():
    username = os.getenv("DIGICASH_API_USER")
    password = os.getenv("DIGICASH_API_PASS")
    if not username or not password:
        raise Exception("DIGICASH_API_USER or DIGICASH_API_PASS not set in the environment.")
    auth_str = f"{username}:{password}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/json",
        "User-Agent": "PnL-AutomationBot/1.0"
    }
    url = "https://api.fastpayph.com/auth"
    resp = requests.post(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Digicash Auth failed: {resp.status_code} {resp.text}")
    data = resp.json()
    if "access_token" not in data:
        raise Exception("No access_token in Digicash response.")
    return data["access_token"]