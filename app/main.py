from fastapi import FastAPI
# from app import model
# from .database import engine
from app import auth
from .routers import patient,staff,appointments,pharmacy,reports,payments,prescriptions


# Create tables in the database
# model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(patient.router, prefix="/patients", tags=["patients"])
app.include_router(staff.router, prefix="/staff", tags=["staff"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(pharmacy.router, prefix="/pharmacy", tags=["pharmacy"]) 
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(prescriptions.router, prefix="/prescriptions", tags=["prescriptions"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Hospital Management System API"}
