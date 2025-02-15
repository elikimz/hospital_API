import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import model, schema, database
from app.database import SessionLocal
from app.auth import get_current_user

router = APIRouter()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Book an appointment
@router.post("/", response_model=schema.AppointmentResponse)
def book_appointment(
    appointment: schema.AppointmentCreate, 
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    # Get all available doctors
    doctors = db.query(model.Staff).filter(model.Staff.department == "Doctor").all()
    
    if not doctors:
        raise HTTPException(status_code=400, detail="No doctors available at the moment")

    # Auto-assign a doctor randomly
    assigned_doctor = random.choice(doctors)

    new_appointment = model.Appointment(
        patient_id=current_user.id,
        doctor_id=assigned_doctor.id,
        date=appointment.date,
        duration=appointment.duration,
        reason=appointment.reason,
        appointment_type=appointment.appointment_type,
        status="pending",
        notes=appointment.notes,
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return new_appointment

# View appointment details
@router.get("/{id}", response_model=schema.AppointmentResponse)
def get_appointment(id: int, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return appointment

# Reschedule appointment
@router.put("/{id}/reschedule", response_model=schema.AppointmentResponse)
def reschedule_appointment(
    id: int,
    appointment_update: schema.AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Only the patient who booked can reschedule
    if db_appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the patient can reschedule this appointment")
    
    # Update appointment details
    db_appointment.date = appointment_update.date
    db_appointment.reason = appointment_update.reason
    db_appointment.notes = appointment_update.notes
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# Cancel appointment
@router.delete("/{id}/cancel")
def cancel_appointment(
    id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Only patient, doctor, or receptionist can cancel
    if current_user.role not in [model.UserRole.PATIENT, model.UserRole.DOCTOR, model.UserRole.RECEPTIONIST]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    db.delete(db_appointment)
    db.commit()
    return {"message": "Appointment canceled successfully"}
