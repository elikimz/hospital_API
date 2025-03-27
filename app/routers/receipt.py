from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app import model, database
from app.auth import get_current_user

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/receipts", response_model=List[Dict])
def get_all_receipts(
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    # Retrieve the patient record associated with the current user
    patient = db.query(model.Patient).filter(model.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Retrieve all payments for this patient
    payments = db.query(model.Payment).filter(model.Payment.patient_id == patient.id).all()
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found for this patient")
    
    # Build a list of receipt data for each payment
    receipts = []
    for payment in payments:
        receipt_data = {
            "hospitalName": "City Hospital",  # You might load this from config or a Hospital model
            "hospitalAddress": "123 Health Blvd, Wellness City",
            "hospitalContact": "555-1234",
            "patientName": patient.full_name,
            "patientId": patient.id,
            "paymentId": payment.id,
            "paymentDate": payment.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(payment, "created_at") else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "paymentMethod": "Stripe Card Payments",
            "amount": payment.amount,
            "notes": "Thank you for your payment!",
        }
        receipts.append(receipt_data)
    
    return receipts
