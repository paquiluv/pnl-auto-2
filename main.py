from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime
from auth import get_digicash_token
from digicash_api import fetch_transactions
from fees import calc_fees
from sheet_manager import authorize_google_sheets, append_or_update_summary

def main():
    client = authorize_google_sheets()
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")

    config_sheet_url = os.getenv("MERCHANT_CONFIG_SHEET_URL")
    if not config_sheet_url:
        raise Exception("MERCHANT_CONFIG_SHEET_URL not set.")
    config_sheet = client.open_by_url(config_sheet_url).sheet1
    merchants = config_sheet.get_all_records()

    token = get_digicash_token()
    for m in merchants:
        if not m.get("Active", True):
            continue
        merchant_id = m.get("merchant_id")
        if not merchant_id or not m.get("sheet_url"):
            print(f"Skipping {m.get('name','UNKNOWN')} (missing merchant_id or sheet_url)")
            continue
        print(f"Processing {m['name']}")
        transactions = fetch_transactions(token, merchant_id, today_str, today_str)
        data = calc_fees(transactions, m)
        target_sheet = client.open_by_url(m["sheet_url"]).sheet1
        append_or_update_summary(target_sheet, today, data)
        print(f"✅ Updated {m['name']} sheet.")
    print("✅ All merchants updated.")

if __name__ == "__main__":
    main()
