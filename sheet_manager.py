import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

REQUIRED_COLUMNS = [
    "Date", "Payins", "Payouts", "GCash Payin Txn", "QRPH Payin Txn", "Payout Txn",
    "GCash Fees", "QRPH Fees", "Payout Fees", "Total Fees", "Buy Rate", "Settlement", "Ending Balance"
]

def authorize_google_sheets():
    with open("service_account.json", "r") as f:
        creds_json = json.load(f)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(credentials)
    return client

def ensure_columns(worksheet):
    existing = worksheet.row_values(1)
    missing = [col for col in REQUIRED_COLUMNS if col not in existing]
    if missing:
        worksheet.append_row(existing + missing)
        print(f"Added missing columns: {missing}")

def append_or_update_summary(sheet, today, data):
    sheet_data = sheet.get_all_records()
    date_str = today.strftime("%m/%d/%Y")
    row_idx = None
    for idx, row in enumerate(sheet_data, start=2):
        if row.get("Date") == date_str:
            row_idx = idx
            break
    if row_idx is None:
        sheet.append_row([date_str] + [""] * (len(REQUIRED_COLUMNS) - 1))
        row_idx = len(sheet.get_all_values())
    values = [
        data["payin_sum"], data["payout_sum"], data["gcash_count"], data["qrph_count"], data["payout_count"],
        data["gcash_fee"], data["qrph_fee"], data["payout_fee"], data["total_fees"], data["buy_rate"]
    ]
    # Insert at columns B-K
    sheet.update(f"B{row_idx}", [values])
    # Settlement is col L (12), Ending Balance is col M (13)
    settlement_val = sheet.cell(row_idx, 12).value
    try:
        settlement = float(settlement_val)
    except Exception:
        settlement = 0.0
    ending_balance = data["payin_sum"] - data["total_fees"] - data["payout_sum"] - settlement
    sheet.update_cell(row_idx, 13, ending_balance)