
#     ]


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import model, database
from app.auth import get_current_user  # Ensure this function is implemented to get the current user

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get daily appointment statistics
@router.get("/appointments/daily")
def get_daily_appointments(db: Session = Depends(get_db)):
    try:
        daily_appointments = (
            db.query(func.date(model.Appointment.date), func.count(model.Appointment.id))
            .group_by(func.date(model.Appointment.date))
            .all()
        )

        return [
            {"date": str(date), "appointments": count} for date, count in daily_appointments
        ]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error processing appointments: {str(e)}")

# ✅ Get payment records for the logged-in user
@router.get("/payments/my-records")
def get_my_payment_records(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    # Assuming payments are linked to users via patient records
    payment_records = (
        db.query(model.Payment)
        .join(model.Patient, model.Payment.patient_id == model.Patient.id)
        .filter(model.Patient.user_id == current_user.id)
        .all()
    )

    if not payment_records:
        raise HTTPException(status_code=404, detail="No payment records found")

    return payment_records

# ✅ Get overall hospital statistics
@router.get("/overview")
def get_hospital_overview(db: Session = Depends(get_db)):
    total_patients = db.query(model.Patient).count()
    total_doctors = db.query(model.User).filter(model.User.role == model.UserRole.DOCTOR).count()
    total_staff = db.query(model.User).filter(model.User.role != model.UserRole.PATIENT).count()
    total_appointments = db.query(model.Appointment).count()
    total_medicines = db.query(model.Medicine).count()

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_staff": total_staff,
        "total_appointments": total_appointments,
        "total_medicines": total_medicines,
    }

# ✅ Get financial summary (Total earnings & pending payments)
@router.get("/financial-summary")
def get_financial_summary(db: Session = Depends(get_db)):
    total_earnings = db.query(func.sum(model.Payment.amount)).scalar() or 0
    total_paid = (
        db.query(func.sum(model.Payment.amount))
        .filter(model.Payment.status == "SUCCESS")
        .scalar()
        or 0
    )
    total_pending = total_earnings - total_paid

    return {
        "total_earnings": total_earnings,
        "total_paid": total_paid,
        "total_pending": total_pending,
    }
