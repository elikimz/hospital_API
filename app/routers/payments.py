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

# Create Stripe Checkout Session
@router.post("/payments/create-checkout-session/")
async def create_checkout_session(db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    print(f"Current User ID: {current_user.id}")  # Log the user ID
    
    # Fetch the patient associated with the current authenticated user
    patient = db.query(model.Patient).filter(model.Patient.user_id == current_user.id).first()
    print(f"Patient found: {patient}")
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Hospital Payment"},
                "unit_amount": 5000,  # Example amount, can be dynamic
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://your-frontend.com/success",
        cancel_url="https://your-frontend.com/cancel",
    )

    # Save payment record in the database
    new_payment = model.Payment(
        patient_id=patient.id,
        amount=50.00,  # Example amount
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
                print(f"Patient Details: ID={patient.id}, Name={patient.full_name}, Contact={patient.contact}")
    
    return {"status": "success"}
