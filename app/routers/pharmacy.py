from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import model
from app.database import get_db
from app.auth import get_current_user
from app.schema import MedicineCreate, MedicineOut

router = APIRouter()


# Add a new medicine
@router.post("/", response_model=MedicineOut)
async def add_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user),
):
    # Ensure only pharmacists or admins can add medicine
    if current_user.role not in [model.UserRole.PHARMACIST, model.UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Only pharmacists or admins can add medicines."
        )

    new_medicine = model.Medicine(
        name=medicine.name,
        # description=medicine.description,
        price=medicine.price,
        stock=medicine.stock,
    )
    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)
    return new_medicine


# Retrieve all medicines
@router.get("/", response_model=list[MedicineOut])
async def get_all_medicines(db: Session = Depends(get_db)):
    medicines = db.query(model.Medicine).all()
    return medicines


# Retrieve a single medicine
@router.get("/{id}", response_model=MedicineOut)
async def get_medicine(id: int, db: Session = Depends(get_db)):
    medicine = db.query(model.Medicine).filter(model.Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")
    return medicine


# Update a medicine
@router.put("/{id}", response_model=MedicineOut)
async def update_medicine(
    id: int,
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user),
):
    # Ensure only pharmacists or admins can update medicines
    if current_user.role not in [model.UserRole.PHARMACIST, model.UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Only pharmacists or admins can update medicines."
        )

    existing_medicine = db.query(model.Medicine).filter(model.Medicine.id == id).first()
    if not existing_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")

    existing_medicine.name = medicine.name
    existing_medicine.description = medicine.description
    existing_medicine.price = medicine.price
    existing_medicine.stock = medicine.stock

    db.commit()
    db.refresh(existing_medicine)
    return existing_medicine


# Delete a medicine
@router.delete("/{id}")
async def delete_medicine(
    id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(get_current_user),
):
    # Ensure only pharmacists or admins can delete medicines
    if current_user.role not in [model.UserRole.PHARMACIST, model.UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Only pharmacists or admins can delete medicines."
        )

    medicine = db.query(model.Medicine).filter(model.Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")

    db.delete(medicine)
    db.commit()
    return {"message": "Medicine deleted successfully."}
