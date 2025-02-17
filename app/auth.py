# # # from fastapi import APIRouter, Depends, HTTPException, status
# # # from sqlalchemy.orm import Session
# # # from sqlalchemy.exc import IntegrityError
# # # from datetime import datetime, timedelta
# # # from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# # # from jose import JWTError, jwt

# # # from app import model, schema, database
# # # from app.utils import verify_password, create_access_token, hash_password
# # # from app.model import UserRole  # Import the UserRole Enum
# # # from app.config import SECRET_KEY, ALGORITHM  # Load from config.py

# # # router = APIRouter()
# # # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# # # # Function to determine user role based on email domain
# # # def assign_role(email: str) -> UserRole:
# # #     if email.endswith("@hospital.com"):
# # #         return UserRole.DOCTOR
# # #     elif email.endswith("@nurse.hospital.com"):
# # #         return UserRole.NURSE
# # #     elif email.endswith("@reception.hospital.com"):
# # #         return UserRole.RECEPTIONIST
# # #     elif email.endswith("@pharmacy.hospital.com"):
# # #         return UserRole.PHARMACIST
# # #     else:
# # #         return UserRole.PATIENT  # Default role


# # # # Dependency to get the current user
# # # def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
# # #     try:
# # #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# # #         email: str = payload.get("sub")
# # #         if email is None:
# # #             raise HTTPException(status_code=401, detail="Invalid token")
        
# # #         user = db.query(model.User).filter(model.User.email == email).first()
# # #         if user is None:
# # #             raise HTTPException(status_code=401, detail="User not found")

# # #         return user
# # #     except JWTError:
# # #         raise HTTPException(status_code=401, detail="Invalid token")
# # #     except Exception as e:
# # #         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# # # # User Registration with Improved Error Handling
# # # @router.post("/register", response_model=schema.User)
# # # def register_user(user: schema.UserCreate, db: Session = Depends(database.get_db)):
# # #     existing_user = db.query(model.User).filter(model.User.email == user.email).first()
# # #     if existing_user:
# # #         raise HTTPException(status_code=400, detail="Email already registered")

# # #     hashed_password = hash_password(user.password)
# # #     assigned_role = assign_role(user.email)

# # #     try:
# # #         new_user = model.User(
# # #             username=user.username,
# # #             email=user.email,
# # #             hashed_password=hashed_password,
# # #             role=assigned_role,
# # #             created_at=datetime.utcnow()
# # #         )
# # #         db.add(new_user)
# # #         db.commit()
# # #         db.refresh(new_user)

# # #         # Create corresponding staff or patient record
# # #         if assigned_role == UserRole.PATIENT:
# # #             new_patient = model.Patient(
# # #                 user_id=new_user.id,
# # #                 full_name=user.username,
# # #                 dob=user.dob,
# # #                 contact=user.contact,
# # #                 created_at=datetime.utcnow()
# # #             )
# # #             db.add(new_patient)
# # #         else:
# # #             new_staff = model.Staff(
# # #                 user_id=new_user.id,
# # #                 full_name=user.username,
# # #                 department=str(assigned_role.value),
# # #                 contact=user.contact,
# # #                 is_active=True,
# # #                 created_at=datetime.utcnow()
# # #             )
# # #             db.add(new_staff)

# # #         db.commit()
# # #         return new_user

# # #     except IntegrityError:
# # #         db.rollback()
# # #         raise HTTPException(status_code=400, detail="A database integrity error occurred. Ensure unique email and valid data.")

# # #     except Exception as e:
# # #         db.rollback()
# # #         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# # # # User Login (JWT Token Generation)
# # # @router.post("/login")
# # # def login(
# # #     form_data: OAuth2PasswordRequestForm = Depends(),
# # #     db: Session = Depends(database.get_db)
# # # ):
# # #     db_user = db.query(model.User).filter(model.User.email == form_data.username).first()
# # #     if not db_user or not verify_password(form_data.password, db_user.hashed_password):
# # #         raise HTTPException(status_code=401, detail="Invalid credentials")
    
# # #     access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(hours=1))
# # #     return {"access_token": access_token, "token_type": "bearer"}


# # # # Get Current User Info
# # # @router.get("/me")
# # # def get_user_info(current_user: model.User = Depends(get_current_user)):
# # #     return {
# # #         "user_id": current_user.id,
# # #         "username": current_user.username,
# # #         "email": current_user.email,
# # #         "role": current_user.role.value
# # #     }


# # # # Update User Role (Admin Only)
# # # @router.put("/update-role/{user_id}")
# # # def update_user_role(
# # #     user_id: int, 
# # #     role: UserRole, 
# # #     db: Session = Depends(database.get_db), 
# # #     current_user: model.User = Depends(get_current_user)
# # # ):
# # #     if current_user.role != UserRole.ADMIN:
# # #         raise HTTPException(status_code=403, detail="Only admin can change user roles")
    
# # #     user = db.query(model.User).filter(model.User.id == user_id).first()
# # #     if not user:
# # #         raise HTTPException(status_code=404, detail="User not found")
    
# # #     user.role = role
# # #     db.commit()
# # #     db.refresh(user)
    
# # #     return {"message": f"User {user.username} role updated to {role.value}. Please log in again."}


# # from fastapi import APIRouter, Depends, HTTPException, status
# # from sqlalchemy.orm import Session
# # from sqlalchemy.exc import IntegrityError
# # from datetime import datetime, timedelta
# # from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# # from jose import JWTError, jwt

# # from app import model, schema, database
# # from app.utils import verify_password, create_access_token, hash_password
# # from app.model import UserRole  # Import the UserRole Enum
# # from app.config import SECRET_KEY, ALGORITHM  # Load from config.py

# # router = APIRouter()
# # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # OAuth2 bearer token for login authentication


# # # Function to determine user role based on email domain
# # def assign_role(email: str) -> UserRole:
# #     """
# #     Assigns a role to a user based on their email domain.
# #     - Admin users: Emails ending with "@admin"
# #     - Doctors: Emails ending with "@hospital.com"
# #     - Nurses: Emails ending with "@nurse.hospital.com"
# #     - Receptionists: Emails ending with "@reception.hospital.com"
# #     - Pharmacists: Emails ending with "@pharmacy.hospital.com"
# #     - Default to Patient if none of the above
# #     """
# #     if email.endswith("@admin"):  # Specific check for Admin role
# #         return UserRole.ADMIN
# #     elif email.endswith("@hospital.com"):
# #         return UserRole.DOCTOR
# #     elif email.endswith("@nurse.hospital.com"):
# #         return UserRole.NURSE
# #     elif email.endswith("@reception.hospital.com"):
# #         return UserRole.RECEPTIONIST
# #     elif email.endswith("@pharmacy.hospital.com"):
# #         return UserRole.PHARMACIST
# #     else:
# #         return UserRole.PATIENT  # Default role if none match


# # # Dependency to get the current user
# # def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
# #     """
# #     Retrieves the current user based on the JWT token passed in the request.
# #     Verifies the token and decodes it to fetch the user's data from the database.
# #     """
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         email: str = payload.get("sub")  # Extract email from token
# #         if email is None:
# #             raise HTTPException(status_code=401, detail="Invalid token")
        
# #         user = db.query(model.User).filter(model.User.email == email).first()
# #         if user is None:
# #             raise HTTPException(status_code=401, detail="User not found")

# #         return user
# #     except JWTError:
# #         raise HTTPException(status_code=401, detail="Invalid token")
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# # # User Registration with Improved Error Handling
# # @router.post("/register", response_model=schema.User)
# # def register_user(user: schema.UserCreate, db: Session = Depends(database.get_db)):
# #     """
# #     Registers a new user by verifying the email, password, and assigning them a role.
# #     If the user is a staff member (doctor, nurse, etc.), a corresponding staff record is created.
# #     If the user is a patient, a corresponding patient record is created.
# #     """
# #     existing_user = db.query(model.User).filter(model.User.email == user.email).first()
# #     if existing_user:
# #         raise HTTPException(status_code=400, detail="Email already registered")

# #     hashed_password = hash_password(user.password)
# #     assigned_role = assign_role(user.email)  # Assign role based on email domain

# #     try:
# #         new_user = model.User(
# #             username=user.username,
# #             email=user.email,
# #             hashed_password=hashed_password,
# #             role=assigned_role,
# #             created_at=datetime.utcnow()
# #         )
# #         db.add(new_user)
# #         db.commit()
# #         db.refresh(new_user)

# #         # Create corresponding staff or patient record
# #         if assigned_role == UserRole.PATIENT:
# #             new_patient = model.Patient(
# #                 user_id=new_user.id,
# #                 full_name=user.username,
# #                 dob=user.dob,
# #                 contact=user.contact,
# #                 created_at=datetime.utcnow()
# #             )
# #             db.add(new_patient)
# #         else:
# #             new_staff = model.Staff(
# #                 user_id=new_user.id,
# #                 full_name=user.username,
# #                 department=str(assigned_role.value),
# #                 contact=user.contact,
# #                 is_active=True,
# #                 created_at=datetime.utcnow()
# #             )
# #             db.add(new_staff)

# #         db.commit()
# #         return new_user

# #     except IntegrityError:
# #         db.rollback()
# #         raise HTTPException(status_code=400, detail="A database integrity error occurred. Ensure unique email and valid data.")

# #     except Exception as e:
# #         db.rollback()
# #         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# # # User Login (JWT Token Generation)
# # @router.post("/login")
# # def login(
# #     form_data: OAuth2PasswordRequestForm = Depends(),
# #     db: Session = Depends(database.get_db)
# # ):
# #     """
# #     User login endpoint that generates and returns a JWT token upon successful authentication.
# #     Verifies the user's email and password and issues a token that can be used for protected routes.
# #     """
# #     db_user = db.query(model.User).filter(model.User.email == form_data.username).first()
# #     if not db_user or not verify_password(form_data.password, db_user.hashed_password):
# #         raise HTTPException(status_code=401, detail="Invalid credentials")
    
# #     access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(hours=1))
# #     return {"access_token": access_token, "token_type": "bearer"}


# # # Get Current User Info
# # @router.get("/me")
# # def get_user_info(current_user: model.User = Depends(get_current_user)):
# #     """
# #     Retrieves information about the currently authenticated user based on the JWT token.
# #     Returns basic user info including ID, username, email, and role.
# #     """
# #     return {
# #         "user_id": current_user.id,
# #         "username": current_user.username,
# #         "email": current_user.email,
# #         "role": current_user.role.value
# #     }


# # # Update User Role (Admin Only)
# # @router.put("/update-role/{user_id}")
# # def update_user_role(
# #     user_id: int, 
# #     role: UserRole, 
# #     db: Session = Depends(database.get_db), 
# #     current_user: model.User = Depends(get_current_user)
# # ):
# #     """
# #     Allows only admin users to update the role of other users.
# #     Admin users can change roles of staff (e.g. Doctor, Nurse, etc.).
# #     """
# #     if current_user.role != UserRole.ADMIN:
# #         raise HTTPException(status_code=403, detail="Only admin can change user roles")
    
# #     user = db.query(model.User).filter(model.User.id == user_id).first()
# #     if not user:
# #         raise HTTPException(status_code=404, detail="User not found")
    
# #     user.role = role
# #     db.commit()
# #     db.refresh(user)
    
# #     return {"message": f"User {user.username} role updated to {role.value}. Please log in again."}


# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from fastapi import APIRouter, Depends, HTTPException, status, Body
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# from app import model, schema, database
# from app.utils import verify_password, create_access_token, hash_password, send_reset_email
# from app.model import UserRole  # Import the UserRole Enum from your models
# from app.config import SECRET_KEY, ALGORITHM  # Configuration file for JWT settings

# router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# # Function to determine user role based on email domain
# def assign_role(email: str) -> UserRole:
#     """
#     Assigns a role to a user based on their email domain.
#       - Admin users: Emails ending with "@admin"
#       - Doctors: Emails ending with "@hospital.com"
#       - Nurses: Emails ending with "@nurse.hospital.com"
#       - Receptionists: Emails ending with "@reception.hospital.com"
#       - Pharmacists: Emails ending with "@pharmacy.hospital.com"
#       - Default to Patient if none of the above
#     """
#     if email.endswith("@admin"):
#         return UserRole.ADMIN
#     elif email.endswith("@hospital.com"):
#         return UserRole.DOCTOR
#     elif email.endswith("@nurse.hospital.com"):
#         return UserRole.NURSE
#     elif email.endswith("@reception.hospital.com"):
#         return UserRole.RECEPTIONIST
#     elif email.endswith("@pharmacy.hospital.com"):
#         return UserRole.PHARMACIST
#     else:
#         return UserRole.PATIENT

# # Dependency to get the current user based on the JWT token.
# def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
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
#         # Create corresponding record in Patient or Staff table based on role.
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
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(database.get_db)
# ):
#     db_user = db.query(model.User).filter(model.User.email == form_data.username).first()
#     if not db_user or not verify_password(form_data.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     access_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(hours=1))
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

# # Password Reset Request Endpoint
# @router.post("/auth/request-reset")
# def request_password_reset(email: str, db: Session = Depends(database.get_db)):
#     user = db.query(model.User).filter(model.User.email == email).first()
#     if not user:
#         # Always return the same response for security
#         return {"message": "If the email is registered, you will receive a password reset link."}
#     expiration = datetime.utcnow() + timedelta(hours=1)
#     reset_token = jwt.encode(
#         {"sub": user.email, "exp": expiration},
#         SECRET_KEY,
#         algorithm=ALGORITHM
#     )
#     send_reset_email(user.email, reset_token)
#     return {"message": "If the email is registered, you will receive a password reset link."}

# # Password Reset Endpoint
# @router.post("/auth/reset-password")
# def reset_password(
#     token: str = Body(..., embed=True),
#     new_password: str = Body(..., embed=True),
#     db: Session = Depends(database.get_db)
# ):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
#     user = db.query(model.User).filter(model.User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
#     user.hashed_password = hash_password(new_password)
#     db.commit()
#     return {"message": "Password reset successfully."}
# #




from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app import model, schema, database
from app.utils import verify_password, create_access_token, hash_password
from app.model import UserRole
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

# Function to determine user role based on email domain

# Dependency to get the current user based on the JWT token.
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
        # Create corresponding record in Patient or Staff table based on role.
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

def create_password_reset_token(email: str):
    expires_delta = timedelta(minutes=30)
    to_encode = {"sub": email, "exp": datetime.utcnow() + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def send_password_reset_email(email: EmailStr, token: str):
    subject = "Password Reset Request"
    body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    background-color: #ffffff;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h2 {{
                    color: #333333;
                    text-align: center;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: #555555;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-top: 20px;
                    text-align: center;
                }}
                .footer {{
                    font-size: 12px;
                    color: #888888;
                    text-align: center;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Please click the link below to reset your password:</p>
                <p><a href="http://yourapp.com/reset-password?token={token}" class="button">Reset Password</a></p>
                <p>This link will expire in 30 minutes.</p>
                <p class="footer">If you did not request this, please ignore this email or contact support.</p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"SMTP Error: {e}")  # Print exact error to debug
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/request-password-reset")
def request_password_reset(email: EmailStr, db: Session = Depends(database.get_db)):
    user = db.query(model.User).filter(model.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_token = create_password_reset_token(email)
    send_password_reset_email(email, reset_token)
    
    return {"message": "Password reset email sent"}