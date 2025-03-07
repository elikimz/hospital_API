from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import model, schema, database, auth
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Create Staff (Only Admins)
@router.post("/", response_model=schema.StaffResponse)
def create_staff(
    staff: schema.StaffCreate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    if current_user.role != model.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can register staff.")

    # 🚨 Prevent unauthorized admin creation
    if staff.role.lower() == "admin":
        raise HTTPException(
            status_code=403, detail="Admin account creation is restricted."
        )

    # Check for existing username or email
    if db.query(model.User).filter(model.User.username == staff.username).first():
        raise HTTPException(status_code=400, detail="Username already exists.")

    if db.query(model.User).filter(model.User.email == staff.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Hash password
    hashed_password = pwd_context.hash(staff.password)

    # Create user account (staff)
    new_user = model.User(
        username=staff.username,
        email=staff.email,
        hashed_password=hashed_password,
        role=model.UserRole(staff.role.lower()),  # Ensure role matches ENUM
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create Staff profile
    new_staff = model.Staff(
        user_id=new_user.id,
        full_name=staff.full_name,
        department=staff.department,
        contact=staff.contact,
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return new_staff


# ✅ Get all staff (Admin & Receptionist Only)
@router.get("/", response_model=list[schema.StaffResponse])
def get_all_staff(
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    if current_user.role not in {model.UserRole.ADMIN, model.UserRole.RECEPTIONIST}:
        raise HTTPException(status_code=403, detail="Unauthorized.")

    return db.query(model.Staff).all()


# ✅ Get staff by ID
@router.get("/{id}", response_model=schema.StaffResponse)
def get_staff(
    id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    staff = db.query(model.Staff).filter(model.Staff.id == id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found.")

    return staff


# ✅ Update staff (Admin Only)
@router.put("/{id}", response_model=schema.StaffResponse)
def update_staff(
    id: int,
    staff: schema.StaffUpdate,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    if current_user.role != model.UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can update staff details."
        )

    db_staff = db.query(model.Staff).filter(model.Staff.id == id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff member not found.")

    # Update allowed fields
    if staff.full_name:
        db_staff.full_name = staff.full_name
    if staff.department:
        db_staff.department = staff.department
    if staff.contact:
        db_staff.contact = staff.contact

    db.commit()
    db.refresh(db_staff)
    return db_staff


# ✅ Delete staff (Admin Only)
@router.delete("/{id}")
def delete_staff(
    id: int,
    db: Session = Depends(get_db),
    current_user: model.User = Depends(auth.get_current_user),
):
    if current_user.role != model.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete staff.")

    db_staff = db.query(model.Staff).filter(model.Staff.id == id).first()
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff member not found.")

    db.delete(db_staff)
    db.commit()
    return {"message": "Staff deleted successfully"}
