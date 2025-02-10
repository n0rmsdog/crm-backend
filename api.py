from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta

# ✅ MongoDB Connection (Loaded from Environment)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true")
client = MongoClient(MONGO_URI)
db = client["crm_backend"]

# ✅ FastAPI App
app = FastAPI()

# ✅ Authentication Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "G1-WlvEmko2Q0oG7H6wIOWUwBx_r0P_gUX8Q5VnrcOU"
ALGORITHM = "HS256"

# ✅ Dummy User Database (Replace with real authentication)
fake_users_db = {
    "admin": {
        "username": "norms",
        "password": "crm",  # ⚠️ Replace with hashed passwords
        "role": "admin"
    }
}

# ✅ Token Generation
def create_access_token(data: dict):
    """Generate a JWT access token."""
    expire = datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Token Verification
def verify_token(token: str = Depends(oauth2_scheme)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Data Models
class Customer(BaseModel):
    name: str
    email: str

# ----------------- ROUTES -----------------

# ✅ Home Route
@app.get("/")
def home():
    return {"message": "Welcome to the CRM API!"}

# ✅ Token Route (Login)
@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# ✅ List Customers (Protected)
@app.get("/customers/")
async def list_customers(token: dict = Depends(verify_token)):
    customers = list(db.customers.find({}, {"_id": 0}))
    return customers

# ✅ Add a Customer (Protected)
@app.post("/customers/")
async def add_customer(customer: Customer, token: dict = Depends(verify_token)):
    db.customers.insert_one(customer.dict())
    return {"message": "Customer added successfully"}
