import os
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from app import model, database
from app.auth import get_current_user
from app.model import PaymentStatus
from fastapi.security import OAuth2PasswordBearer

# Load environment variables
load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
    raise ValueError("Stripe API keys are missing. Check your .env file.")

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()

# OAuth2 Bearer token dependency for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to calculate the patient's bill (implement logic based on your system)
def calculate_patient_bill(patient_id: int, db: Session) -> float:
    # Example calculation based on prescriptions, appointments, etc.
    prescriptions = db.query(model.Prescription).filter(model.Prescription.patient_id == patient_id).all()
    appointment_fees = 0  # Example of appointment fees calculation

    total_bill = appointment_fees
    for prescription in prescriptions:
        total_bill += prescription.medicine.price  # Add the medicine price for each prescription

    return total_bill

# Create Stripe Checkout Session
@router.post("/payments/create-checkout-session/")
async def create_checkout_session(db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    print(f"Current User ID: {current_user.id}")  # Log the user ID
    
    # Fetch the patient associated with the current authenticated user
    patient = db.query(model.Patient).filter(model.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Calculate the patient's total bill dynamically
    patient_total_bill = calculate_patient_bill(patient.id, db)
    if patient_total_bill <= 0:
        raise HTTPException(status_code=400, detail="Invalid bill amount")

    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Hospital Payment"},
                "unit_amount": int(patient_total_bill * 100),  # Convert to cents
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"https://your-frontend.com/payment-success/{patient.id}",
        cancel_url=f"https://your-frontend.com/payment-failed/{patient.id}",
    )

    # Save payment record in the database
    new_payment = model.Payment(
        patient_id=patient.id,
        amount=patient_total_bill,
        stripe_session_id=session.id,
        status=model.PaymentStatus.PENDING,
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {"checkout_url": session.url}

@router.post("/webhook/")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Find payment in database
        payment = db.query(model.Payment).filter(model.Payment.stripe_session_id == session["id"]).first()
        if payment:
            payment.status = PaymentStatus.SUCCESS
            db.commit()

            # Find the patient associated with the payment
            patient = db.query(model.Patient).filter(model.Patient.id == payment.patient_id).first()
            if patient:
                print(f"Payment successful for Patient: ID={patient.id}, Name={patient.full_name}, Contact={patient.contact}")
    
    return {"status": "success"}
