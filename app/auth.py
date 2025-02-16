from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app import model, schema, database
from app.utils import verify_password, create_access_token, hash_password
from app.model import UserRole  # Import the UserRole Enum
from app.config import SECRET_KEY, ALGORITHM  # Load from config.py

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Function to determine user role based on email domain
def assign_role(email: str) -> UserRole:
    if email.endswith("@hospital.com"):
        return UserRole.DOCTOR
    elif email.endswith("@nurse.hospital.com"):
        return UserRole.NURSE
    elif email.endswith("@reception.hospital.com"):
        return UserRole.RECEPTIONIST
    elif email.endswith("@pharmacy.hospital.com"):
        return UserRole.PHARMACIST
    else:
        return UserRole.PATIENT  # Default role


# Dependency to get the current user
def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(model.User).filter(model.User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# User Registration with Improved Error Handling
@router.post("/register", response_model=schema.User)
def register_user(user: schema.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(model.User).filter(model.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    assigned_role = assign_role(user.email)

    try:
        new_user = model.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=assigned_role,
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create corresponding staff or patient record
        if assigned_role == UserRole.PATIENT:
            new_patient = model.Patient(
                user_id=new_user.id,
                full_name=user.username,
                dob=user.dob,
                contact=user.contact,
                created_at=datetime.utcnow()
            )
            db.add(new_patient)
        else:
            new_staff = model.Staff(
                user_id=new_user.id,
                full_name=user.username,
                department=str(assigned_role.value),
                contact=user.contact,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(new_staff)

        db.commit()
        return new_user

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A database integrity error occurred. Ensure unique email and valid data.")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# User Login (JWT Token Generation)
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    db_user = db.query(model.User).filter(model.User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}


# Get Current User Info
@router.get("/me")
def get_user_info(current_user: model.User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value
    }


# Update User Role (Admin Only)
@router.put("/update-role/{user_id}")
def update_user_role(
    user_id: int, 
    role: UserRole, 
    db: Session = Depends(database.get_db), 
    current_user: model.User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can change user roles")
    
    user = db.query(model.User).filter(model.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = role
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {user.username} role updated to {role.value}. Please log in again."}
