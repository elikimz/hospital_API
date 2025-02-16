from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import model, schema, database
from app.auth import get_current_user
from app.model import UserRole

router = APIRouter()

# Dependency to check if the current user is an admin or doctor.
def check_if_admin_or_doctor(current_user: model.User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create, update or delete a patient."
        )

# Endpoint to create a new patient.
@router.post("/patients/", response_model=schema.Patient)
def create_patient(
    patient: schema.PatientCreate,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    check_if_admin_or_doctor(current_user)

    new_patient = model.Patient(
        full_name=patient.full_name,
        dob=patient.dob,
        contact=patient.contact,
        user_id=current_user.id
    )

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient

# Endpoint to get a patient by their ID.
@router.get("/patients/{id}", response_model=schema.Patient)
def get_patient(id: int, db: Session = Depends(database.get_db)):
    patient = db.query(model.Patient).filter(model.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# Endpoint to delete a patient record.
@router.delete("/patients/{id}", response_model=schema.Patient)
def delete_patient(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete a patient."
        )
    
    patient = db.query(model.Patient).filter(model.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return patient

# Endpoint to get all patients (accessible only by Admin or Doctor).
@router.get("/patients/", response_model=List[schema.Patient])
def get_all_patients(
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view all patients."
        )
    patients = db.query(model.Patient).all()
    return patients

# Endpoint to reschedule an appointment (allowing any authenticated user to reschedule).
@router.put("/appointments/{appointment_id}", response_model=schema.AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    appointment_update: schema.AppointmentUpdate,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    # Fetch the appointment.
    db_appointment = db.query(model.Appointment).filter(model.Appointment.id == appointment_id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Removed ownership check: any authenticated user can reschedule.
    
    # Update the appointment details.
    db_appointment.date = appointment_update.date
    db_appointment.reason = appointment_update.reason
    db_appointment.notes = appointment_update.notes

    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# Endpoint to cancel an appointment.
@router.delete("/appointments/{id}/cancel")
def cancel_appointment(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Only patient, doctor, or receptionist can cancel.
    if current_user.role not in [UserRole.PATIENT, UserRole.DOCTOR, UserRole.RECEPTIONIST]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

    db.delete(db_appointment)
    db.commit()
    return {"message": "Appointment canceled successfully"}
