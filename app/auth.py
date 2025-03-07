

# import random
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError
# from datetime import datetime, timedelta
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose import JWTError, jwt
# from pydantic import BaseModel, EmailStr
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# from app import model, schema, database
# from app.utils import verify_password, create_access_token, hash_password
# from app.model import User, UserRole
# from app.config import SECRET_KEY, ALGORITHM, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

# router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# # Function to determine user role based on email domain
# def assign_role(email: str) -> UserRole:
#     if email.endswith("@hospital.com"):
#         return UserRole.DOCTOR
#     elif email.endswith("@nurse.hospital.com"):
#         return UserRole.NURSE
#     elif email.endswith("@reception.hospital.com"):
#         return UserRole.RECEPTIONIST
#     elif email.endswith("@pharmacy.hospital.com"):
#         return UserRole.PHARMACIST
#     else:
#         return UserRole.PATIENT  # Default role

# # Dependency to get the current user based on the JWT token.
# def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         role: str = payload.get("role")
#         if email is None or role is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         user = db.query(model.User).filter(model.User.email == email).first()
#         if user is None:
#             raise HTTPException(status_code=401, detail="User not found")
#         return user
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# # Registration Endpoint
# @router.post("/register", response_model=schema.User)
# def register_user(user: schema.UserCreate, db: Session = Depends(database.get_db)):
#     existing_user = db.query(model.User).filter(model.User.email == user.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     hashed_password = hash_password(user.password)
#     assigned_role = assign_role(user.email)
#     try:
#         new_user = model.User(
#             username=user.username,
#             email=user.email,
#             hashed_password=hashed_password,
#             role=assigned_role,
#             created_at=datetime.utcnow()
#         )
#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)
#         if assigned_role == UserRole.PATIENT:
#             new_patient = model.Patient(
#                 user_id=new_user.id,
#                 full_name=user.username,
#                 dob=user.dob,
#                 contact=user.contact,
#                 created_at=datetime.utcnow()
#             )
#             db.add(new_patient)
#         else:
#             new_staff = model.Staff(
#                 user_id=new_user.id,
#                 full_name=user.username,
#                 department=str(assigned_role.value),
#                 contact=user.contact,
#                 is_active=True,
#                 created_at=datetime.utcnow()
#             )
#             db.add(new_staff)
#         db.commit()
#         return new_user
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="A database integrity error occurred. Ensure unique email and valid data.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# # Login Endpoint (JWT Token Generation)
# @router.post("/login")
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(database.get_db)
# ):
#     db_user = db.query(model.User).filter(model.User.email == form_data.username).first()
#     if not db_user or not verify_password(form_data.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     access_token = create_access_token(data={"sub": db_user.email, "role": db_user.role.value}, expires_delta=timedelta(hours=1))
#     return {"access_token": access_token, "token_type": "bearer"}

# # Get Current User Info
# @router.get("/me")
# def get_user_info(current_user: model.User = Depends(get_current_user)):
#     return {
#         "user_id": current_user.id,
#         "username": current_user.username,
#         "email": current_user.email,
#         "role": current_user.role.value
    
#     }

# # Update User Role (Admin Only)

# @router.put("/update-role/{user_id}")
# def update_user_role(
#     user_id: int,
#     role: UserRole,
#     db: Session = Depends(database.get_db),
#     current_user: model.User = Depends(get_current_user)
# ):
#     if current_user.role != UserRole.ADMIN:
#         raise HTTPException(status_code=403, detail="Only admin can change user roles")
#     user = db.query(model.User).filter(model.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user.role = role
#     db.commit()
#     db.refresh(user)
#     return {"message": f"User {user.username} role updated to {role.value}. Please log in again."}


# class ChangePasswordRequest(BaseModel):
#     old_password: str
#     new_password: str

# @router.post("/change-password")
# def change_password(request: ChangePasswordRequest, db: Session = Depends(database.get_db), current_user: model.User = Depends(get_current_user)):
#     if not verify_password(request.old_password, current_user.hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect old password")

#     hashed_password = hash_password(request.new_password)
#     current_user.hashed_password = hashed_password
#     db.commit()
#     db.refresh(current_user)

#     return {"message": "Password changed successfully"}




# # In-memory store for OTPs
# otp_store = {}

# class PasswordResetRequest(BaseModel):
#     email: EmailStr

# class PasswordResetVerify(BaseModel):
#     email: EmailStr
#     otp: str
#     new_password: str

# class ChangePasswordRequest(BaseModel):
#     old_password: str
#     new_password: str


# def send_otp_email(email: str, otp: str):
#     subject = "Your Password Reset OTP"
#     body = f"Your OTP for password reset is: {otp}. It will expire in 10 minutes."

#     msg = MIMEMultipart()
#     msg['From'] = SMTP_USERNAME
#     msg['To'] = email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(SMTP_USERNAME, SMTP_PASSWORD)
#             server.sendmail(SMTP_USERNAME, email, msg.as_string())
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


# @router.post("/request-password-reset")
# def request_password_reset(request: PasswordResetRequest, db: Session = Depends(database.get_db)):
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     otp = str(random.randint(100000, 999999))
#     otp_store[request.email] = {"otp": otp, "expires_at": datetime.utcnow() + timedelta(minutes=10)}
#     send_otp_email(request.email, otp)

#     return {"message": "OTP sent to your email."}


# @router.post("/verify-otp-reset-password")
# def verify_otp_reset_password(request: PasswordResetVerify, db: Session = Depends(database.get_db)):
#     if request.email not in otp_store:
#         raise HTTPException(status_code=400, detail="No OTP request found for this email")
    
#     stored_otp_data = otp_store[request.email]
#     if datetime.utcnow() > stored_otp_data['expires_at']:
#         del otp_store[request.email]
#         raise HTTPException(status_code=400, detail="OTP expired")
    
#     if stored_otp_data['otp'] != request.otp:
#         raise HTTPException(status_code=400, detail="Invalid OTP")
    
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     user.hashed_password = hash_password(request.new_password)
#     db.commit()
#     db.refresh(user)
#     del otp_store[request.email]

#     return {"message": "Password reset successful"}


# @router.post("/change-password")
# def change_password(request: ChangePasswordRequest, db: Session = Depends(database.get_db), current_user: model.User = Depends(get_current_user)):
#     if not verify_password(request.old_password, current_user.hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect old password")

#     current_user.hashed_password = hash_password(request.new_password)
#     db.commit()
#     db.refresh(current_user)

#     return {"message": "Password changed successfully"}



import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app import model, schema, database
from app.utils import verify_password, create_access_token, hash_password
from app.model import User, UserRole
from app.config import SECRET_KEY, ALGORITHM, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

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

# Dependency to get the current user based on the JWT token.
def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(model.User).filter(model.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Registration Endpoint
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

# Login Endpoint (JWT Token Generation)
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    db_user = db.query(model.User).filter(model.User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email, "user_id": db_user.id, "role": db_user.role.value}, expires_delta=timedelta(hours=1))
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

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, db: Session = Depends(database.get_db), current_user: model.User = Depends(get_current_user)):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    hashed_password = hash_password(request.new_password)
    current_user.hashed_password = hashed_password
    db.commit()
    db.refresh(current_user)

    return {"message": "Password changed successfully"}

# In-memory store for OTPs
otp_store = {}

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetVerify(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

def send_otp_email(email: str, otp: str):
    subject = "Your Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}. It will expire in 10 minutes."

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@router.post("/request-password-reset")
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(database.get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))
    otp_store[request.email] = {"otp": otp, "expires_at": datetime.utcnow() + timedelta(minutes=10)}
    send_otp_email(request.email, otp)

    return {"message": "OTP sent to your email."}

@router.post("/verify-otp-reset-password")
def verify_otp_reset_password(request: PasswordResetVerify, db: Session = Depends(database.get_db)):
    if request.email not in otp_store:
        raise HTTPException(status_code=400, detail="No OTP request found for this email")

    stored_otp_data = otp_store[request.email]
    if datetime.utcnow() > stored_otp_data['expires_at']:
        del otp_store[request.email]
        raise HTTPException(status_code=400, detail="OTP expired")

    if stored_otp_data['otp'] != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(request.new_password)
    db.commit()
    db.refresh(user)
    del otp_store[request.email]

    return {"message": "Password reset successful"}
