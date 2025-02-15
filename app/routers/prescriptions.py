from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import model
from app.database import get_db
from app.auth import get_current_user
from app.schema import PrescriptionCreate, PrescriptionOut

router = APIRouter()

# Create a Prescription
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import model
from app.database import get_db
from app.auth import get_current_user
from app.schema import PrescriptionCreate, PrescriptionOut

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

    # Patient ID should be passed in the body by the frontend
    patient_id = prescription.patient_id
    
    # Check if the patient exists
    patient = db.query(model.Patient).filter(model.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    
    # Check if the medicine exists
    medicine = db.query(model.Medicine).filter(model.Medicine.id == prescription.medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")

    # Create the prescription with doctor and patient details
    new_prescription = model.Prescription(
        doctor_id=current_user.id,  # Automatically assigned from the logged-in doctor
        patient_id=patient_id,  # Patient passed from the frontend
        medicine_id=prescription.medicine_id,  # Passed from the frontend
        dosage=prescription.dosage
    )

    # Save to database
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)

    return new_prescription


# View a Prescription
@router.get("/prescriptions/{id}", response_model=PrescriptionOut)
async def get_prescription(id: int, db: Session = Depends(get_db)):
    prescription = db.query(model.Prescription).filter(model.Prescription.id == id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found.")
    return prescription

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

    return existing_prescription

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