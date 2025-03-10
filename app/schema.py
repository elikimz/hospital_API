


# from datetime import date, datetime
# from typing import Optional
# from pydantic import BaseModel, EmailStr
# from enum import Enum

# # -------------------------------
# # User Schemas
# # -------------------------------
# class RoleEnum(str, Enum):
#     admin = "admin"
#     doctor = "doctor"
#     nurse = "nurse"
#     receptionist = "receptionist"
#     pharmacist = "pharmacist"
#     patient = "patient"

# class UserBase(BaseModel):
#     username: str
#     email: str

# class UserCreate(BaseModel):
#     username: str
#     email: EmailStr
#     password: str
#     dob: date
#     contact: str
#     full_name: str

# class UserLogin(BaseModel):
#     email: str
#     password: str

# class User(UserBase):
#     id: int

#     class Config:
#         orm_mode = True

# # -------------------------------
# # Patient Schemas
# # -------------------------------
# class PatientCreate(BaseModel):
#     full_name: str
#     dob: datetime
#     contact: str

#     class Config:
#         orm_mode = True

# class Patient(BaseModel):
#     id: int
#     full_name: str
#     dob: datetime
#     contact: str

#     class Config:
#         orm_mode = True

# class PatientUpdate(BaseModel):
#     full_name: str
#     dob: date  # Enforces a proper date format
#     contact: str

# class PatientWithUser(Patient):
#     user: User

#     class Config:
#         orm_mode = True

# # -------------------------------
# # Staff Schemas
# # -------------------------------
# class UserRoleEnum(str, Enum):
#     ADMIN = "admin"
#     DOCTOR = "doctor"
#     NURSE = "nurse"
#     RECEPTIONIST = "receptionist"
#     PHARMACIST = "pharmacist"
#     PATIENT = "patient"

# class StaffCreate(BaseModel):
#     username: str
#     email: EmailStr
#     password: str
#     full_name: str
#     department: str
#     contact: str
#     role: UserRoleEnum

# class StaffUpdate(BaseModel):
#     full_name: Optional[str] = None
#     department: Optional[str] = None
#     contact: Optional[str] = None

# class StaffResponse(BaseModel):
#     id: int
#     full_name: str
#     department: str
#     contact: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# # -------------------------------
# # Appointment Schemas
# # -------------------------------
# class AppointmentCreate(BaseModel):
#     date: datetime
#     duration: int = 30
#     reason: str
#     doctor_id: int
#     appointment_type: str = "physical"
#     notes: Optional[str] = None

# class AppointmentUpdate(BaseModel):
#     date: datetime
#     reason: str
#     notes: Optional[str] = None

# class AppointmentReschedule(BaseModel):
#     date: datetime
#     reason: str
#     notes: Optional[str] = None

# class AppointmentResponse(BaseModel):
#     id: int
#     patient_id: int
#     doctor_id: int
#     date: datetime
#     duration: int
#     reason: str
#     appointment_type: str
#     status: str
#     notes: Optional[str] = None
#     created_at: datetime

#     class Config:
#         from_attributes = True

# class AppointmentResponseWithPatient(AppointmentResponse):
#     patient: PatientWithUser

#     class Config:
#         orm_mode = True

# # -------------------------------
# # Medicine Schemas
# # -------------------------------
# class MedicineCreate(BaseModel):
#     name: str
#     stock: int
#     price: float
#     description: str

# class MedicineUpdate(BaseModel):
#     name: Optional[str] = None
#     stock: Optional[int] = None
#     price: Optional[float] = None

# class MedicineResponse(BaseModel):
#     id: int
#     name: str
#     stock: int
#     price: float
#     created_at: datetime

#     class Config:
#         orm_mode = True

# class MedicineOut(BaseModel):
#     id: int
#     name: str
#     stock: int
#     price: float
#     created_at: datetime

#     class Config:
#         orm_mode = True

# # -------------------------------
# # Prescription Schemas
# # -------------------------------
# class PrescriptionBase(BaseModel):
#     medicine_id: int
#     dosage: str

#     class Config:
#         orm_mode = True

# class PrescriptionCreate(BaseModel):
#     patient_name: str
#     medicine_name: str
#     dosage: str

#     class Config:
#         orm_mode = True

# class PrescriptionOut(BaseModel):
#     id: int
#     doctor_id: int
#     patient_id: int
#     medicine_id: int
#     patient_name: str  # Added field
#     medicine_name: str  # Added field
#     dosage: str
#     created_at: str

#     class Config:
#         orm_mode = True

#     @classmethod
#     def from_orm(cls, obj):
#         obj_dict = obj.__dict__
#         obj_dict["created_at"] = obj.created_at.isoformat()
#         return super().from_orm(obj)


from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

# -------------------------------
# User Schemas
# -------------------------------
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

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    dob: date
    contact: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

# -------------------------------
# Patient Schemas
# -------------------------------
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

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None  # Enforces a proper date format
    contact: Optional[str] = None

class PatientWithUser(Patient):
    user: User

    class Config:
        orm_mode = True

# -------------------------------
# Staff Schemas
# -------------------------------
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    PHARMACIST = "pharmacist"
    PATIENT = "patient"

class StaffCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    department: str
    contact: str
    role: UserRoleEnum

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    contact: Optional[str] = None

class StaffResponse(BaseModel):
    id: int
    full_name: str
    department: str
    contact: str
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------------
# Appointment Schemas
# -------------------------------
class AppointmentCreate(BaseModel):
    date: datetime
    duration: int = 30
    reason: str
    doctor_id: int
    appointment_type: str = "physical"
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    date: datetime
    reason: str
    notes: Optional[str] = None

class AppointmentReschedule(BaseModel):
    date: datetime
    reason: str
    notes: Optional[str] = None

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

class AppointmentResponseWithPatient(AppointmentResponse):
    patient: PatientWithUser

    class Config:
        orm_mode = True

# -------------------------------
# Medicine Schemas
# -------------------------------
class MedicineCreate(BaseModel):
    name: str
    stock: int
    price: float
    description: str

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    stock: Optional[int] = None
    price: Optional[float] = None

class MedicineResponse(BaseModel):
    id: int
    name: str
    stock: int
    price: float
    created_at: datetime

    class Config:
        orm_mode = True

class MedicineOut(BaseModel):
    id: int
    name: str
    stock: int
    price: float
    created_at: datetime

    class Config:
        orm_mode = True

# -------------------------------
# Prescription Schemas
# -------------------------------
class PrescriptionBase(BaseModel):
    medicine_id: int
    dosage: str

    class Config:
        orm_mode = True

class PrescriptionCreate(BaseModel):
    patient_name: str
    medicine_name: str
    dosage: str

    class Config:
        orm_mode = True

class PrescriptionOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    medicine_id: int
    patient_name: str  # Added field
    medicine_name: str  # Added field
    dosage: str
    created_at: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        obj_dict = obj.__dict__
        obj_dict["created_at"] = obj.created_at.isoformat()
        return super().from_orm(obj)
