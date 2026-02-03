import re
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

API_KEY = "mysecretkey123"

def extract_upi(text: str):
    match = re.search(r'\b[\w.-]+@[\w.-]+\b', text)
    return match.group(0) if match else None

def extract_url(text: str):
    match = re.search(r'https?://\S+|www\.\S+', text)
    return match.group(0) if match else None

def extract_bank_account(text: str):
    match = re.search(r'\b\d{9,18}\b', text)
    return match.group(0) if match else None

@app.post("/analyze")
def analyze_message(data: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    message = data.get("message", "")

    upi = extract_upi(message)
    url = extract_url(message)
    bank_account = extract_bank_account(message)

    scam = any([upi, url, bank_account]) or any(
        word in message.lower()
        for word in ["kyc", "blocked", "urgent", "verify", "click", "suspended"]
    )

    if upi:
        reply = "This UPI seems important. Which bank is it linked to?"
    elif url:
        reply = "I clicked the link but need more details. What is this for?"
    elif bank_account:
        reply = "Please confirm the bank name for this account."
    else:
        reply = "Can you share more details regarding this message?"

    return {
        "is_scam": scam,
        "agent_reply": reply,
        "extracted_data": {
            "upi_id": upi,
            "bank_account": bank_account,
            "url": url
        }
    }
