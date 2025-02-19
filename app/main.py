from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app import auth
from .routers import patient, staff, appointments, pharmacy, reports, payments, prescriptions,SMS

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, change to a specific domain if necessary
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers for various routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(patient.router, prefix="/patients", tags=["patients"])
app.include_router(staff.router, prefix="/staff", tags=["staff"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(pharmacy.router, prefix="/pharmacy", tags=["pharmacy"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(prescriptions.router, prefix="/prescriptions", tags=["prescriptions"])
app.include_router(SMS.router, prefix="/sms", tags=["sms"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hospital Management System API"}
