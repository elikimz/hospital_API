from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app import schema

# Password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# JWT token generation
SECRET_KEY = "your_"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# from passlib.context import CryptContext
# import bcrypt
# from datetime import datetime, timedelta
# from jose import JWTError, jwt

# # Set up password hashing context using bcrypt
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     """Hash a plain text password."""
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """Verify a plain text password against a hashed password."""
#     return pwd_context.verify(plain_password, hashed_password)

# JWT token generation: note that SECRET_KEY and ALGORITHM are imported from config in auth.py,
# so here we assume they are defined in the configuration file.
# def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
#     """
#     Create a JWT access token.
#     `data` should include the subject, e.g., {"sub": user.email}.
#     """
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})
#     # SECRET_KEY and ALGORITHM should come from your config (they are imported in auth.py)
#     from app.config import SECRET_KEY, ALGORITHM
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def send_reset_email(email: str, token: str):
#     """
#     Dummy function to simulate sending a password reset email.
#     In a real application, integrate with an email service provider.
#     """
#     reset_link = f"https://hospital-management-frontend-gray.vercel.app//reset-password?token={token}"
#     print(f"Send email to {email} with reset link: {reset_link}")
    
