# sms_router.py
import os
import africastalking
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Africa's Talking
username = os.getenv("AT_USERNAME")
api_key = os.getenv("AT_API_KEY")

africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Initialize the router
router = APIRouter()

# Request model
class SMSRequest(BaseModel):
    phone_number: str
    message: str

@router.post("/send_sms")
async def send_sms(request: SMSRequest):
    try:
        # Sending SMS through Africa's Talking
        response = sms.send(request.message, [request.phone_number])
        return {"status": "success", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
