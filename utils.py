import os, csv, re, json
from datetime import datetime

LEADS_CSV = os.environ.get("LEADS_CSV", "data/leads.csv")

def ensure_csv():
    os.makedirs(os.path.dirname(LEADS_CSV), exist_ok=True)
    if not os.path.exists(LEADS_CSV):
        with open(LEADS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts","name","company","phone","email","city","notes"])

def save_lead(lead_dict, notes=""):
    ensure_csv()
    row = [
        datetime.utcnow().isoformat(),
        lead_dict.get("name",""),
        lead_dict.get("company",""),
        lead_dict.get("phone",""),
        lead_dict.get("email",""),
        lead_dict.get("city",""),
        notes
    ]
    with open(LEADS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

# --- Google Sheets opcional ---
SHEETS_ID = os.environ.get("GOOGLE_SHEETS_ID","")
SERVICE_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON","")

def write_to_sheet(lead_dict, notes=""):
    if not SHEETS_ID or not SERVICE_JSON:
        return False
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(json.loads(SERVICE_JSON), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(SHEETS_ID)
        ws = sh.sheet1
        row = [
            datetime.utcnow().isoformat(),
            lead_dict.get("name",""),
            lead_dict.get("company",""),
            lead_dict.get("phone",""),
            lead_dict.get("email",""),
            lead_dict.get("city",""),
            notes
        ]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception:
        return False

def sanitize_user_text(t):
    return re.sub(r"[\r\n]+"," ", t).strip()

def to_agent_json(message, lead_update=None, next_actions=None):
    return {
        "message": message.strip(),
        "lead_update": lead_update or None,
        "next_actions": next_actions or []
    }
