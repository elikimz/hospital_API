# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app import model, schema, database
# from app.auth import get_current_user
# from app.model import UserRole

# router = APIRouter()

# # Dependency to check if the current user is an admin or doctor.
# def check_if_admin_or_doctor(current_user: model.User = Depends(get_current_user)):
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to create, update or delete a patient."
#         )

# # Endpoint to create a new patient.
# @router.post("/patients/", response_model=schema.Patient)
# def create_patient(
#     patient: schema.PatientCreate,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     check_if_admin_or_doctor(current_user)

#     new_patient = model.Patient(
#         full_name=patient.full_name,
#         dob=patient.dob,
#         contact=patient.contact,
#         user_id=current_user.id
#     )

#     db.add(new_patient)
#     db.commit()
#     db.refresh(new_patient)
#     return new_patient

# # Endpoint to get a patient by their ID.
# @router.get("/patients/{id}", response_model=schema.Patient)
# def get_patient(id: int, db: Session = Depends(database.get_db)):
#     patient = db.query(model.Patient).filter(model.Patient.id == id).first()
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     return patient

# # Endpoint to delete a patient record.
# @router.delete("/patients/{id}", response_model=schema.Patient)
# def delete_patient(
#     id: int,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     if current_user.role != UserRole.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to delete a patient."
#         )
    
#     patient = db.query(model.Patient).filter(model.Patient.id == id).first()
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
    
#     db.delete(patient)
#     db.commit()
#     return patient

# # Endpoint to get all patients (accessible only by Admin or Doctor).
# @router.get("/patients/", response_model=List[schema.Patient])
# def get_all_patients(
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to view all patients."
#         )
#     patients = db.query(model.Patient).all()
#     return patients

# # Endpoint to reschedule an appointment (allowing any authenticated user to reschedule).
# @router.put("/appointments/{appointment_id}", response_model=schema.AppointmentResponse)
# def reschedule_appointment(
#     appointment_id: int,
#     appointment_update: schema.AppointmentUpdate,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     # Fetch the appointment.
#     db_appointment = db.query(model.Appointment).filter(model.Appointment.id == appointment_id).first()
    
#     if not db_appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")
    
#     # Removed ownership check: any authenticated user can reschedule.
    
#     # Update the appointment details.
#     db_appointment.date = appointment_update.date
#     db_appointment.reason = appointment_update.reason
#     db_appointment.notes = appointment_update.notes

#     db.commit()
#     db.refresh(db_appointment)
#     return db_appointment

# # Endpoint to cancel an appointment.
# @router.delete("/appointments/{id}/cancel")
# def cancel_appointment(
#     id: int,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    
#     if not db_appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")

#     # Only patient, doctor, or receptionist can cancel.
#     if current_user.role not in [UserRole.PATIENT, UserRole.DOCTOR, UserRole.RECEPTIONIST]:
#         raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

#     db.delete(db_appointment)
#     db.commit()
#     return {"message": "Appointment canceled successfully"}



# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from datetime import datetime
# from pydantic import BaseModel
# from app import model, schema, database
# from app.auth import get_current_user
# from app.model import UserRole

# router = APIRouter()

# # Dependency to check if the current user is an admin or doctor.
# def check_if_admin_or_doctor(current_user: model.User = Depends(get_current_user)):
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to create, update or delete an appointment."
#         )

# # Endpoint to create a new appointment.
# @router.post("/", response_model=schema.AppointmentResponse)
# def create_appointment(
#     appointment: schema.AppointmentCreate,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to create an appointment."
#         )

#     patient_id = None
#     doctor_id = None

#     # Automatically set patient or doctor ID
#     if current_user.role == UserRole.PATIENT:
#         patient_id = current_user.id
#     elif current_user.role == UserRole.DOCTOR:
#         doctor_id = current_user.id

#     # Admins need to pass both patient and doctor IDs
#     if current_user.role == UserRole.ADMIN:
#         if not appointment.patient_id or not appointment.doctor_id:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Admin must provide both patient_id and doctor_id."
#             )
#         patient_id = appointment.patient_id
#         doctor_id = appointment.doctor_id

#     new_appointment = model.Appointment(
#         patient_id=patient_id,
#         doctor_id=doctor_id,
#         date=appointment.date,
#         duration=appointment.duration,
#         reason=appointment.reason,
#         appointment_type=appointment.appointment_type,
#         status="pending",
#         notes=appointment.notes,
#         created_at=datetime.utcnow()
#     )

#     db.add(new_appointment)
#     db.commit()
#     db.refresh(new_appointment)
#     return new_appointment

# # Endpoint to get an appointment by its ID.
# @router.get("/{id}", response_model=schema.AppointmentResponse)
# def get_appointment(id: int, db: Session = Depends(database.get_db)):
#     appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
#     if not appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")
#     return appointment

# # Endpoint to update an appointment.
# @router.put("/{id}", response_model=schema.AppointmentResponse)
# def update_appointment(
#     id: int,
#     appointment_update: schema.AppointmentUpdate,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     check_if_admin_or_doctor(current_user)

#     db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
#     if not db_appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")

#     db_appointment.date = appointment_update.date
#     db_appointment.reason = appointment_update.reason
#     db_appointment.notes = appointment_update.notes

#     db.commit()
#     db.refresh(db_appointment)
#     return db_appointment

# # Endpoint to delete an appointment.
# @router.delete("/{id}", response_model=schema.AppointmentResponse)
# def delete_appointment(
#     id: int,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     if current_user.role != UserRole.ADMIN:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to delete an appointment."
#         )

#     appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
#     if not appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")

#     db.delete(appointment)
#     db.commit()
#     return appointment

# # Endpoint to get all appointments (accessible only by Admin or Doctor).
# @router.get("/", response_model=List[schema.AppointmentResponse])
# def get_all_appointments(
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to view all appointments."
#         )
#     appointments = db.query(model.Appointment).all()
#     return appointments

# # Endpoint to reschedule an appointment (allowing any authenticated user to reschedule).
# @router.put("/{appointment_id}/reschedule", response_model=schema.AppointmentResponse)
# def reschedule_appointment(
#     appointment_id: int,
#     appointment_update: schema.AppointmentReschedule,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     db_appointment = db.query(model.Appointment).filter(model.Appointment.id == appointment_id).first()

#     if not db_appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")

#     db_appointment.date = appointment_update.date
#     db_appointment.reason = appointment_update.reason
#     db_appointment.notes = appointment_update.notes

#     db.commit()
#     db.refresh(db_appointment)
#     return db_appointment

# # Endpoint to cancel an appointment.
# @router.delete("/{id}/cancel")
# def cancel_appointment(
#     id: int,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()

#     if not db_appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")

#     if current_user.role not in [UserRole.PATIENT, UserRole.DOCTOR, UserRole.RECEPTIONIST]:
#         raise HTTPException(status_code=403, detail="Not authorized to cancel this appointment")

#     db.delete(db_appointment)
#     db.commit()
#     return {"message": "Appointment canceled successfully"}



from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app import model, schema, database
from app.auth import get_current_user
from app.model import UserRole

router = APIRouter()


def check_if_admin_or_doctor(current_user: model.User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create, update or delete an appointment."
        )


@router.post("/", response_model=schema.AppointmentResponse)
def create_appointment(
    appointment: schema.AppointmentCreate,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR, UserRole.PATIENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create an appointment."
        )

    patient_id = None
    doctor_id = None

    if current_user.role == UserRole.PATIENT:
        patient_id = current_user.id
        doctor_id = appointment.doctor_id
        if not doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient must select a doctor for the appointment."
            )

    elif current_user.role == UserRole.DOCTOR:
        doctor_id = current_user.id
        patient_id = appointment.patient_id
        if not patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor must specify a patient for the appointment."
            )

    if current_user.role == UserRole.ADMIN:
        if not appointment.patient_id or not appointment.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin must provide both patient_id and doctor_id."
            )
        patient_id = appointment.patient_id
        doctor_id = appointment.doctor_id

    if not patient_id or not doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both patient_id and doctor_id are required to create an appointment."
        )

    new_appointment = model.Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        date=appointment.date,
        duration=appointment.duration,
        reason=appointment.reason,
        appointment_type=appointment.appointment_type,
        status="pending",
        notes=appointment.notes,
        created_at=datetime.utcnow()
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@router.get("/{id}", response_model=schema.AppointmentResponse)
def get_appointment(id: int, db: Session = Depends(database.get_db)):
    appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.put("/{id}", response_model=schema.AppointmentResponse)
def update_appointment(
    id: int,
    appointment_update: schema.AppointmentUpdate,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    check_if_admin_or_doctor(current_user)
    
    db_appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db_appointment.date = appointment_update.date
    db_appointment.reason = appointment_update.reason
    db_appointment.notes = appointment_update.notes

    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@router.delete("/{id}", response_model=schema.AppointmentResponse)
def delete_appointment(
    id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete an appointment."
        )

    appointment = db.query(model.Appointment).filter(model.Appointment.id == id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()
    return appointment


@router.get("/", response_model=List[schema.AppointmentResponse])
def get_all_appointments(
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view all appointments."
        )
    appointments = db.query(model.Appointment).all()
    return appointments
