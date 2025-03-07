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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper function to calculate the patient’s bill
def calculate_patient_bill(patient_id: int, db: Session) -> float:
    prescriptions = (
        db.query(model.Prescription)
        .filter(model.Prescription.patient_id == patient_id)
        .all()
    )
    appointment_fees = 50

    print(f"Found {len(prescriptions)} prescriptions for Patient ID: {patient_id}")
    for prescription in prescriptions:
        print(
            f"Prescription ID: {prescription.id}, Medicine ID: {prescription.medicine_id}"
        )
        appointment_fees += prescription.medicine.price

    return appointment_fees


# Create Stripe Checkout Session
@router.post("/payments/create-checkout-session/")
async def create_checkout_session(
    db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)
):
    print(f"Current User ID: {current_user.id}")

    patient = (
        db.query(model.Patient).filter(model.Patient.user_id == current_user.id).first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    print(f"Patient ID: {patient.id}, Full Name: {patient.full_name}")

    patient_total_bill = calculate_patient_bill(patient.id, db)
    if patient_total_bill <= 0:
        raise HTTPException(status_code=400, detail="Invalid bill amount")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Hospital Payment"},
                    "unit_amount": int(patient_total_bill * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"https://your-frontend.com/payment-success/{patient.id}",
        cancel_url=f"https://your-frontend.com/payment-failed/{patient.id}",
    )

    new_payment = model.Payment(
        patient_id=patient.id,
        amount=patient_total_bill,
        stripe_session_id=session.id,
        status=model.PaymentStatus.PENDING,
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    print(
        f"Payment record created: Payment ID: {new_payment.id}, Amount: {new_payment.amount}"
    )

    return {"checkout_url": session.url}


# Stripe Webhook
@router.post("/webhook/")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        payment = (
            db.query(model.Payment)
            .filter(model.Payment.stripe_session_id == session["id"])
            .first()
        )
        if payment:
            payment.status = PaymentStatus.SUCCESS
            db.commit()

            patient = (
                db.query(model.Patient)
                .filter(model.Patient.id == payment.patient_id)
                .first()
            )
            if patient:
                print(
                    f"Payment successful for Patient: ID={patient.id}, Name={patient.full_name}"
                )
                prescriptions = (
                    db.query(model.Prescription)
                    .filter(model.Prescription.patient_id == patient.id)
                    .all()
                )

                if prescriptions:
                    for prescription in prescriptions:
                        print(
                            f"Prescription ID: {prescription.id}, Medicine ID: {prescription.medicine_id}"
                        )
                else:
                    print(f"No prescriptions found for Patient ID: {patient.id}")

    return {"status": "success"}
