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

# 📌 Book an appointment
@router.post("/", response_model=schema.AppointmentResponse)
def book_appointment(
    appointment: schema.AppointmentCreate, 
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    # ✅ Ensure only patients can book an appointment
    if current_user.role != model.UserRole.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can book appointments")

    # ✅ Check if the patient exists in the patients table
    patient = db.query(model.Patient).filter(model.Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Patient record not found. Please register as a patient first.")

    # ✅ Get all available doctors
    doctors = db.query(model.Staff).filter(model.Staff.department.ilike("%doctor%"), model.Staff.is_active == True).all()
    if not doctors:
        raise HTTPException(status_code=400, detail="No available doctors at the moment")

    # ✅ Auto-assign a doctor randomly
    assigned_doctor = random.choice(doctors)

    new_appointment = model.Appointment(
        patient_id=patient.id,  # ✅ Use patient.id from the patients table
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

# 📌 View a single appointment
@router.get("/{id}", response_model=schema.AppointmentResponse)
def get_appointment(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # ✅ Authorization: Only the patient, assigned doctor, receptionist, or admin can view the appointment
    if (
        current_user.role == model.UserRole.PATIENT and appointment.patient_id != current_user.id
    ) and (
        current_user.role == model.UserRole.DOCTOR and appointment.doctor_id != current_user.id
    ) and (
        current_user.role not in [model.UserRole.RECEPTIONIST, model.UserRole.ADMIN]
    ):
        raise HTTPException(status_code=403, detail="You are not authorized to view this appointment")
    
    return appointment

# 📌 View all appointments (for authorized roles)
@router.get("/", response_model=list[schema.AppointmentResponse])
def get_all_appointments(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    # ✅ Patients can only see their own appointments
    if current_user.role == model.UserRole.PATIENT:
        return db.query(model.Appointment).filter(model.Appointment.patient_id == current_user.id).all()
    
    # ✅ Doctors can only see their assigned appointments
    if current_user.role == model.UserRole.DOCTOR:
        return db.query(model.Appointment).filter(model.Appointment.doctor_id == current_user.id).all()
    
    # ✅ Receptionists and Admins can see all appointments
    if current_user.role in [model.UserRole.RECEPTIONIST, model.UserRole.ADMIN]:
        return db.query(model.Appointment).all()
    
    raise HTTPException(status_code=403, detail="You are not authorized to view appointments")

# 📌 Reschedule appointment
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
    
    # ✅ Only the patient who booked can reschedule
    if current_user.role == model.UserRole.PATIENT and db_appointment.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the patient can reschedule this appointment")
    
    # ✅ Update appointment details
    db_appointment.date = appointment_update.date
    db_appointment.reason = appointment_update.reason
    db_appointment.notes = appointment_update.notes
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# 📌 Cancel appointment
@router.delete("/{id}/cancel")
def cancel_appointment(
    id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # ✅ Only patient, doctor, or receptionist can cancel
    if current_user.role not in [model.UserRole.PATIENT, model.UserRole.DOCTOR, model.UserRole.RECEPTIONIST]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    db.delete(db_appointment)
    db.commit()
    return {"message": "Appointment canceled successfully"}
