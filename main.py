from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# Import your NLP functions
from reminder_engine import reminder_engine, learn_from_user_correction

# -----------------------------------
# Initialize App
# -----------------------------------
app = FastAPI(
    title="Reminder Extraction API",
    description="API for extracting and learning reminders",
    version="1.0.0"
)

# -----------------------------------
# Enable CORS
# -----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# Request Models
# -----------------------------------
class ReminderRequest(BaseModel):
    text: str = Field(..., example="Remind me to call mom at home")
    friend_list: List[str] = Field(default=[])


class LearnRequest(BaseModel):
    original_text: str
    action: str
    location: str
    person: str


# -----------------------------------
# Root
# -----------------------------------
@app.get("/")
def home():
    return {
        "message": "Reminder API is running 🚀",
        "status": "success"
    }


# -----------------------------------
# 1️⃣ Extract Reminder (ONLY extraction)
# -----------------------------------
@app.post("/extract_reminder")
def extract_reminder(req: ReminderRequest):
    try:
        result = reminder_engine(req.text, req.friend_list)

        if not result:
            raise HTTPException(status_code=400, detail="Unable to process request")

        return {
            "result": result,
            "message": "Check if this is correct (YES/NO in frontend)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# 2️⃣ Learn ONLY when user says NO
# -----------------------------------
@app.post("/learn")
def learn(req: LearnRequest):
    try:
        corrected_output = {
            "intent": "location_based_reminder",
            "action": req.action,
            "location": req.location,
            "person": req.person,
            "confidence": 1.0
        }

        # Store correction
        learn_from_user_correction(req.original_text, corrected_output)

        return {
            "message": "Correction learned successfully ✅",
            "corrected_output": corrected_output
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))