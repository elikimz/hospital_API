from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import model, schema, database
from app.auth import get_current_user
from app.model import UserRole

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Get all medicines
@router.get("/", response_model=list[schema.MedicineResponse])
def get_all_medicines(
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    medicines = db.query(model.Medicine).all()
    return medicines

# ✅ Add a new medicine
@router.post("/", response_model=schema.MedicineResponse, status_code=status.HTTP_201_CREATED)
def add_medicine(
    medicine: schema.MedicineCreate, 
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.PHARMACIST]:
        raise HTTPException(status_code=403, detail="Only admins or pharmacists can add medicines")

    new_medicine = model.Medicine(**medicine.model_dump())
    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)
    return new_medicine

# ✅ Get medicine details
@router.get("/{id}", response_model=schema.MedicineResponse)
def get_medicine(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    medicine = db.query(model.Medicine).filter(model.Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

# ✅ Update medicine stock
@router.put("/{id}", response_model=schema.MedicineResponse)
def update_medicine(
    id: int, 
    update_data: schema.MedicineUpdate,  # Use MedicineUpdate schema for partial updates
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.PHARMACIST]:
        raise HTTPException(status_code=403, detail="Only admins or pharmacists can update medicine details")

    medicine = db.query(model.Medicine).filter(model.Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(medicine, key, value)

    db.commit()
    db.refresh(medicine)
    return medicine

# ✅ Remove a medicine
@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_medicine(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.PHARMACIST]:
        raise HTTPException(status_code=403, detail="Only admins or pharmacists can remove medicines")

    medicine = db.query(model.Medicine).filter(model.Medicine.id == id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    db.delete(medicine)
    db.commit()
    return {"message": "Medicine removed successfully"}
