from datetime import datetime
import enum
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    doctor = "doctor"
    nurse = "nurse"
    receptionist = "receptionist"
    pharmacist = "pharmacist"
    patient = "patient"

class UserBase(BaseModel):
    username: str
    email: str
    role: Optional[str] = None
    # role: RoleEnum

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# Pydantic schema for creating a new patient
class PatientCreate(BaseModel):
    full_name: str
    dob: datetime
    contact: str

    class Config:
        orm_mode = True

class Patient(BaseModel):
    id: int
    full_name: str
    dob: datetime
    contact: str

    class Config:
        orm_mode = True

# Enum for staff roles
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PHARMACIST = "pharmacist"
    PATIENT = "patient"

# Staff creation schema
class StaffCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    department: str
    contact: str
    role: UserRoleEnum

# Staff update schema
class StaffUpdate(BaseModel):
    full_name: str | None = None
    department: str | None = None
    contact: str | None = None

# Staff response schema
class StaffResponse(BaseModel):
    id: int
    full_name: str
    department: str
    contact: str
    created_at: datetime

    class Config:
        from_attributes = True


# Schema for creating an appointment
class AppointmentCreate(BaseModel):
    date: datetime
    duration: int = 30  # Default duration is 30 minutes
    reason: str
    appointment_type: str = "physical"  # Default to physical appointment
    notes: Optional[str] = None

# Schema for updating an appointment
class AppointmentUpdate(BaseModel):
    date: datetime
    reason: str
    notes: Optional[str] = None

# Schema for appointment response
class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    date: datetime
    duration: int
    reason: str
    appointment_type: str
    status: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True



# ✅ Schema for Creating Medicine
class MedicineCreate(BaseModel):
    name: str
    stock: int
    price: float

# ✅ Schema for Updating Medicine (Partial Updates Allowed)
class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    stock: Optional[int] = None
    price: Optional[float] = None

# ✅ Schema for Response
class MedicineResponse(BaseModel):
    id: int
    name: str
    stock: int
    price: float
    created_at: datetime  # ✅ Include timestamp

    class Config:
        orm_mode = True  # ✅ This allows SQLAlchemy models to be converted to Pydantic


# Base schema for response
class PrescriptionBase(BaseModel):
    medicine_id: int
    dosage: str

    class Config:
        orm_mode = True

# Base schema for response
class PrescriptionBase(BaseModel):
    medicine_id: int
    dosage: str

    class Config:
        orm_mode = True

# Base schema for response
class PrescriptionBase(BaseModel):
    medicine_id: int
    dosage: str

    class Config:
        orm_mode = True

# PrescriptionCreate schema
class PrescriptionCreate(BaseModel):
    patient_id: int  # Patient to whom the prescription is assigned
    medicine_id: int  # Medicine prescribed
    dosage: str  # Dosage instructions

    class Config:
        orm_mode = True

# PrescriptionOut schema
class PrescriptionOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    medicine_id: int
    dosage: str
    created_at: datetime

    class Config:
        orm_mode = True