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

@router.get("/receipt/{payment_id}", response_model=dict)
def get_receipt(payment_id: int, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    # Retrieve the payment record
    payment = db.query(model.Payment).filter(model.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Retrieve patient information (assuming patient details are stored in the Patient model)
    patient = db.query(model.Patient).filter(model.Patient.id == payment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Build receipt data
    receipt_data = {
        "hospitalName": "City Hospital",  # You might load this from config or a Hospital model
        "hospitalAddress": "123 Health Blvd, Wellness City",
        "hospitalContact": "555-1234",
        "patientName": patient.full_name,
        "patientId": patient.id,
        "paymentId": payment.id,
        "paymentDate": payment.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(payment, "created_at") else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "paymentMethod": "Stripe Card Payment",
        "amount": payment.amount,
        "notes": "Thank you for your payment!",
    }
    
    return receipt_data
