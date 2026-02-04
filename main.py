import re
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

# ---------- ROOT CHECK ----------
@app.get("/")
def root():
    return {
        "status": "honeypot-api is live",
        "message": "Use POST /analyze to scan messages"
    }

# ---------- API KEY ----------
API_KEY = "mysecretkey123"

# ---------- ANALYZE ENDPOINT ----------
@app.post("/analyze")
def analyze_message(data: dict, x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    message = data.get("message", "")

    # Extract patterns
    upi_match = re.search(r"\b[\w.-]+@[\w.-]+\b", message)
    url_match = re.search(r"https?://\S+", message)

    upi = upi_match.group(0) if upi_match else None
    url = url_match.group(0) if url_match else None

    scam_keywords = ["kyc", "blocked", "urgent", "verify", "click", "suspended"]
    keyword_flag = any(word in message.lower() for word in scam_keywords)

    is_scam = bool(upi or url or keyword_flag)

    if upi:
        reply = "This UPI seems important. Which bank is it linked to?"
    elif url:
        reply = "A link was detected. What is this link for?"
    else:
        reply = "Please share more details about this message."

    return {
        "is_scam": is_scam,
        "agent_reply": reply,
        "extracted_data": {
            "upi_id": upi,
            "bank_account": None,
            "url": url
        }
    }
