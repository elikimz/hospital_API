# from typing import List
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app import model, schema, database
# from app.auth import get_current_user
# from app.model import UserRole

# router = APIRouter()

# # Dependency to check if user is admin or doctor
# def check_if_admin_or_doctor(current_user: model.User = Depends(get_current_user)):
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to create, update or delete a patient."
#         )



# @router.get("/", response_model=List[schema.Patient])
# def get_all_patients(db: Session = Depends(database.get_db), 
#                      current_user: model.User = Depends(get_current_user)):
#     # Only Admin or Doctor can view all patients
#     if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permissionn to view all patients."
#         )
    
#     # Fetch all patients
#     patients = db.query(model.Patient).all()
#     return patients



# @router.get("/{id}", response_model=schema.Patient)
# def get_patient(id: int, db: Session = Depends(database.get_db)):
#     patient = db.query(model.Patient).filter(model.Patient.id == id).first()
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
    
#     return patient



# # Delete patient record
# @router.delete("/{id}", response_model=schema.Patient)
# def delete_patient(id: int, db: Session = Depends(database.get_db), 
#                    current_user: model.User = Depends(get_current_user)):
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



from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import DataError
from app import model, schema, database
from app.auth import get_current_user
from app.model import UserRole

router = APIRouter()


# Dependency to check if user is admin or doctor
def check_if_admin_or_doctor(current_user: model.User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create, update or delete a patient."
        )


@router.get("/", response_model=List[schema.Patient])
def get_all_patients(db: Session = Depends(database.get_db),
                     current_user: model.User = Depends(get_current_user)):
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view all patients."
        )

    patients = db.query(model.Patient).all()
    return patients


@router.get("/{id}", response_model=schema.Patient)
def get_patient(id: int, db: Session = Depends(database.get_db)):
    patient = db.query(model.Patient).filter(model.Patient.id == id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.put("/{id}", response_model=schema.Patient)
def update_patient(id: int, patient_data: schema.PatientUpdate, 
                   db: Session = Depends(database.get_db),
                   current_user: model.User = Depends(get_current_user)):
    patient = db.query(model.Patient).filter(model.Patient.id == id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if current_user.role not in [UserRole.ADMIN, UserRole.DOCTOR] and current_user.id != patient.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this patient."
        )

    try:
        for key, value in patient_data.dict(exclude_unset=True).items():
            setattr(patient, key, value)
        
        db.commit()
        db.refresh(patient)
        return patient

    except DataError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format. Please check your inputs."
        )


@router.delete("/{id}", response_model=schema.Patient)
def delete_patient(id: int, db: Session = Depends(database.get_db),
                   current_user: model.User = Depends(get_current_user)):
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


# Let me know if you want any more tweaks or improvements! 🚀
