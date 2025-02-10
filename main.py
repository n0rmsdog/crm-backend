import os
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from pydantic import BaseModel

# ✅ Force Render to Use Port 8000
PORT = 8000

# ✅ Load MongoDB Connection from Environment
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["crm_backend"]

# ✅ Define MongoDB Collections
customers_collection = db["customers"]
jobs_collection = db["jobs"]
invoices_collection = db["invoices"]
calendar_collection = db["calendar"]
gps_collection = db["gps_tracking"]
users_collection = db["users"]

# ✅ Authentication Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "G1-WlvEmko2Q0oG7H6wIOWUwBx_r0P_gUX8Q5VnrcOU"
ALGORITHM = "HS256"

# ✅ User Database (For Testing Purposes)
fake_users_db = {
    "admin": {"username": "norms", "password": "crm", "role": "admin"}
}

# ✅ Initialize FastAPI App
app = FastAPI()

# ----------------- ✅ AUTHENTICATION -----------------

def create_access_token(data: dict):
    """Generate a JWT access token."""
    expire = datetime.utcnow() + timedelta(days=7)  # 7-day expiration
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and generate JWT token."""
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# ----------------- ✅ CUSTOMERS -----------------

class Customer(BaseModel):
    name: str
    email: str

@app.post("/customers/")
async def create_customer(customer: Customer, token: dict = Depends(verify_token)):
    customers_collection.insert_one(customer.dict())
    return {"message": "Customer added successfully"}

@app.get("/customers/")
async def get_customers(token: dict = Depends(verify_token)):
    customers = list(customers_collection.find({}, {"_id": 0}))
    return customers

# ----------------- ✅ JOBS -----------------

class Job(BaseModel):
    title: str
    description: str
    assigned_to: str

@app.post("/jobs/")
async def create_job(job: Job, token: dict = Depends(verify_token)):
    jobs_collection.insert_one(job.dict())
    return {"message": "Job added successfully"}

@app.get("/jobs/")
async def get_jobs(token: dict = Depends(verify_token)):
    jobs = list(jobs_collection.find({}, {"_id": 0}))
    return jobs

# ----------------- ✅ INVOICES -----------------

class Invoice(BaseModel):
    customer: str
    amount: float
    status: str  # Paid, Unpaid, Pending

@app.post("/invoices/")
async def create_invoice(invoice: Invoice, token: dict = Depends(verify_token)):
    invoices_collection.insert_one(invoice.dict())
    return {"message": "Invoice added successfully"}

@app.get("/invoices/")
async def get_invoices(token: dict = Depends(verify_token)):
    invoices = list(invoices_collection.find({}, {"_id": 0}))
    return invoices

# ----------------- ✅ CALENDAR -----------------

class Event(BaseModel):
    title: str
    date: str  # YYYY-MM-DD
    details: str

@app.post("/calendar/")
async def create_event(event: Event, token: dict = Depends(verify_token)):
    calendar_collection.insert_one(event.dict())
    return {"message": "Event added successfully"}

@app.get("/calendar/")
async def get_events(token: dict = Depends(verify_token)):
    events = list(calendar_collection.find({}, {"_id": 0}))
    return events

# ----------------- ✅ GPS TRACKING -----------------

class GPSData(BaseModel):
    user: str
    latitude: float
    longitude: float
    timestamp: str

@app.post("/gps/")
async def save_gps_data(gps_data: GPSData, token: dict = Depends(verify_token)):
    gps_collection.insert_one(gps_data.dict())
    return {"message": "GPS data saved successfully"}

@app.get("/gps/")
async def get_gps_data(token: dict = Depends(verify_token)):
    gps_data = list(gps_collection.find({}, {"_id": 0}))
    return gps_data

# ----------------- ✅ USERS -----------------

class User(BaseModel):
    username: str
    password: str

@app.post("/users/")
async def create_user(user: User, token: dict = Depends(verify_token)):
    """Register a new user."""
    users_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.get("/users/")
async def get_users(token: dict = Depends(verify_token)):
    """Get list of users."""
    users = list(users_collection.find({}, {"_id": 0}))
    return users

# ----------------- ✅ PROTECTED ROUTES -----------------

@app.get("/protected")
async def protected_route(token: dict = Depends(verify_token)):
    """A protected route requiring authentication."""
    return {"message": "You have access to this route"}

# ✅ Welcome Route
@app.get("/")
def home():
    return {"message": "Welcome to the CRM API!"}
