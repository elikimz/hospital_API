from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import model, database
from app.auth import get_current_user
from app.model import UserRole

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get overall hospital statistics
@router.get("/")
def get_hospital_overview(
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        raise HTTPException(status_code=403, detail="Only admins or receptionists can view the dashboard")

    total_patients = db.query(model.Patient).count()
    total_doctors = db.query(model.User).filter(model.User.role == UserRole.DOCTOR).count()
    total_staff = db.query(model.User).filter(model.User.role != UserRole.PATIENT).count()
    total_appointments = db.query(model.Appointment).count()
    total_medicines = db.query(model.Medicine).count()

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_staff": total_staff,
        "total_appointments": total_appointments,
        "total_medicines": total_medicines
    }

# ✅ Get financial summary (Total earnings & pending payments)
@router.get("/")
def get_financial_summary(
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
        raise HTTPException(status_code=403, detail="Only admins or accountants can view financial reports")

    # Assuming model.Billing exists or should be replaced with model.Payment
    total_earnings = db.query(func.sum(model.Payment.amount)).scalar() or 0
    total_paid = db.query(func.sum(model.Payment.amount)).filter(model.Payment.status == "SUCCESS").scalar() or 0
    total_pending = total_earnings - total_paid

    return {
        "total_earnings": total_earnings,
        "total_paid": total_paid,
        "total_pending": total_pending
    }

# ✅ Get daily appointment statistics
@router.get("/")
def get_daily_appointments(
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST, UserRole.DOCTOR]:
        raise HTTPException(status_code=403, detail="Only authorized staff can view appointments")

    daily_appointments = (
        db.query(func.date(model.Appointment.date), func.count(model.Appointment.id))
        .group_by(func.date(model.Appointment.date))
        .all()
    )

    return [{"date": str(date), "appointments": count} for date, count in daily_appointments]
