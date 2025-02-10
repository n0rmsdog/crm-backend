import os
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pydantic import BaseModel

# ✅ FORCE Render to Use Port 8000
PORT = 8000

# ✅ Constants
SECRET_KEY = "G1-WlvEmko2Q0oG7H6wIOWUwBx_r0P_gUX8Q5VnrcOU"
ALGORITHM = "HS256"

# ✅ Initialize FastAPI App
app = FastAPI()

# ✅ MongoDB Connection (Updated URI)
MONGO_URI = "mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["crm_backend"]

# Collections
customers_collection = db["customers"]
jobs_collection = db["jobs"]
invoices_collection = db["invoices"]
calendar_collection = db["calendar"]
gps_collection = db["gps_tracking"]

# ✅ OAuth2 Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ----------------- AUTH ROUTES -----------------
@app.post("/token")
async def login():
    token = create_access_token({"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}

# ----------------- CUSTOMER ROUTES -----------------
class Customer(BaseModel):
    name: str
    email: str

@app.post("/customers/")
async def create_customer(customer: Customer, token: str = Depends(verify_token)):
    customers_collection.insert_one(customer.dict())
    return {"message": "Customer added successfully"}

@app.get("/customers/")
async def get_customers(token: str = Depends(verify_token)):
    customers = list(customers_collection.find({}, {"_id": 0}))
    return customers

# ----------------- JOB ROUTES -----------------
class Job(BaseModel):
    title: str
    description: str
    assigned_to: str

@app.post("/jobs/")
async def create_job(job: Job, token: str = Depends(verify_token)):
    jobs_collection.insert_one(job.dict())
    return {"message": "Job added successfully"}

@app.get("/jobs/")
async def get_jobs(token: str = Depends(verify_token)):
    jobs = list(jobs_collection.find({}, {"_id": 0}))
    return jobs

# ----------------- INVOICE ROUTES -----------------
class Invoice(BaseModel):
    customer: str
    amount: float
    status: str  # Paid, Unpaid, Pending

@app.post("/invoices/")
async def create_invoice(invoice: Invoice, token: str = Depends(verify_token)):
    invoices_collection.insert_one(invoice.dict())
    return {"message": "Invoice added successfully"}

@app.get("/invoices/")
async def get_invoices(token: str = Depends(verify_token)):
    invoices = list(invoices_collection.find({}, {"_id": 0}))
    return invoices

# ----------------- CALENDAR ROUTES -----------------
class Event(BaseModel):
    title: str
    date: str  # YYYY-MM-DD
    details: str

@app.post("/calendar/")
async def create_event(event: Event, token: str = Depends(verify_token)):
    calendar_collection.insert_one(event.dict())
    return {"message": "Event added successfully"}

@app.get("/calendar/")
async def get_events(token: str = Depends(verify_token)):
    events = list(calendar_collection.find({}, {"_id": 0}))
    return events

# ----------------- GPS TRACKING ROUTES -----------------
class GPSData(BaseModel):
    user: str
    latitude: float
    longitude: float
    timestamp: str

@app.post("/gps/")
async def save_gps_data(gps_data: GPSData, token: str = Depends(verify_token)):
    gps_collection.insert_one(gps_data.dict())
    return {"message": "GPS data saved successfully"}

@app.get("/gps/")
async def get_gps_data(token: str = Depends(verify_token)):
    gps_data = list(gps_collection.find({}, {"_id": 0}))
    return gps_data

# ----------------- PROTECTED TEST ROUTE -----------------
@app.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    return {"message": "You have access to this route"}
