from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import model
from app.database import get_db
from app.auth import get_current_user
from app.schema import PrescriptionCreate, PrescriptionOut
from datetime import datetime

router = APIRouter()

# Create a Prescription
@router.post("/prescriptions/", response_model=PrescriptionOut)
async def create_prescription(
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    # Ensure the current user is a doctor
    if current_user.role != model.UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can create prescriptions.")
    
    # Fetch patient and medicine by name
    patient = db.query(model.Patient).filter(model.Patient.full_name == prescription.patient_name).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    medicine = db.query(model.Medicine).filter(model.Medicine.name == prescription.medicine_name).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")
    
    # Ensure the current user is a doctor and exists in the staff table
    doctor = db.query(model.Staff).filter(model.Staff.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found.")
    
    # Create the prescription with doctor and patient details
    new_prescription = model.Prescription(
        doctor_id=doctor.id,  # Set the doctor_id from the logged-in doctor
        patient_id=patient.id,  # Patient ID fetched from the database
        medicine_id=medicine.id,  # Medicine ID fetched from the database
        dosage=prescription.dosage,
        created_at=datetime.utcnow()  # Set the created_at timestamp
    )

    # Save to database
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)

    # Convert created_at to string before returning the response
    new_prescription_dict = new_prescription.__dict__
    new_prescription_dict["created_at"] = new_prescription_dict["created_at"].strftime('%Y-%m-%d %H:%M:%S')

    return new_prescription_dict

# View a Prescription
@router.get("/prescriptions/{id}", response_model=PrescriptionOut)
async def get_prescription(id: int, db: Session = Depends(get_db)):
    prescription = db.query(model.Prescription).filter(model.Prescription.id == id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found.")

    # Convert created_at to string before returning the response
    prescription_dict = prescription.__dict__
    prescription_dict["created_at"] = prescription_dict["created_at"].strftime('%Y-%m-%d %H:%M:%S')

    return prescription_dict

# Update a Prescription
@router.put("/prescriptions/{id}", response_model=PrescriptionOut)
async def update_prescription(
    id: int,
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user)
):
    # Ensure that only doctors can update prescriptions
    if current_user.role != model.UserRole.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can update prescriptions.")

    existing_prescription = db.query(model.Prescription).filter(model.Prescription.id == id).first()
    if not existing_prescription:
        raise HTTPException(status_code=404, detail="Prescription not found.")

    # Update the dosage
    existing_prescription.dosage = prescription.dosage
    db.commit()
    db.refresh(existing_prescription)

    # Convert created_at to string before returning the response
    existing_prescription_dict = existing_prescription.__dict__
    existing_prescription_dict["created_at"] = existing_prescription_dict["created_at"].strftime('%Y-%m-%d %H:%M:%S')

    return existing_prescription_dict

# Delete a Prescription
@router.delete("/prescriptions/{id}")
async def delete_prescription(id: int, db: Session = Depends(get_db), current_user: model.User = Depends(get_current_user)):
    # Ensure that only doctors or admins can delete prescriptions
    if current_user.role not in [model.UserRole.DOCTOR, model.UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only doctors or admins can delete prescriptions.")

    prescription = db.query(model.Prescription).filter(model.Prescription.id == id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found.")

    db.delete(prescription)
    db.commit()

    return {"message": "Prescription deleted successfully."}
