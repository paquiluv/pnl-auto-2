import requests
import time

def fetch_transactions(token, merchant_id, start_date, end_date):
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "PnL-AutomationBot/1.0"
    }
    url = f"https://api.fastpayph.com/transactions?merchantId={merchant_id}&startDate={start_date}&endDate={end_date}"
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            return resp.json().get("transactions", [])
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)