from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
from pymongo import MongoClient
from pydantic import BaseModel

# ✅ Environment Variables (Render uses $PORT)
PORT = int(os.environ.get("PORT", 8000))

# ✅ Constants
SECRET_KEY = "G1-WlvEmko2Q0oG7H6wIOWUwBx_r0P_gUX8Q5VnrcOU"
ALGORITHM = "HS256"

# ✅ FastAPI App
app = FastAPI()

# ✅ MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["crm_database"]
customers_collection = db["customers"]
jobs_collection = db["jobs"]
invoices_collection = db["invoices"]
gps_collection = db["gps_tracking"]
calendar_collection = db["calendar"]

# ✅ OAuth2 Token Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ✅ Authentication Functions
def create_access_token(data: dict):
    """Generate a permanent JWT token."""
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

# ✅ Models
class Customer(BaseModel):
    name: str
    email: str

class Job(BaseModel):
    title: str
    description: str
    assigned_to: str

class Invoice(BaseModel):
    customer: str
    amount: float
    status: str

class GPSTrack(BaseModel):
    user: str
    latitude: float
    longitude: float

class CalendarEvent(BaseModel):
    title: str
    date: str
    details: str

# ✅ Authentication Route
@app.post("/token")
async def login():
    """Generate and return a permanent JWT token."""
    token = create_access_token({"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}

# ✅ Customer Routes
@app.post("/customers/")
async def create_customer(customer: Customer, token: str = Depends(verify_token)):
    customers_collection.insert_one(customer.dict())
    return {"message": "Customer added successfully"}

@app.get("/customers/")
async def get_customers(token: str = Depends(verify_token)):
    customers = list(customers_collection.find({}, {"_id": 0}))
    return customers

# ✅ Job Routes
@app.post("/jobs/")
async def create_job(job: Job, token: str = Depends(verify_token)):
    jobs_collection.insert_one(job.dict())
    return {"message": "Job created successfully"}

@app.get("/jobs/")
async def get_jobs(token: str = Depends(verify_token)):
    jobs = list(jobs_collection.find({}, {"_id": 0}))
    return jobs

# ✅ Invoice Routes
@app.post("/invoices/")
async def create_invoice(invoice: Invoice, token: str = Depends(verify_token)):
    invoices_collection.insert_one(invoice.dict())
    return {"message": "Invoice created successfully"}

@app.get("/invoices/")
async def get_invoices(token: str = Depends(verify_token)):
    invoices = list(invoices_collection.find({}, {"_id": 0}))
    return invoices

# ✅ GPS Tracking Routes
@app.post("/gps/")
async def track_gps(gps: GPSTrack, token: str = Depends(verify_token)):
    gps_collection.insert_one(gps.dict())
    return {"message": "GPS data saved"}

@app.get("/gps/")
async def get_gps_data(token: str = Depends(verify_token)):
    gps_data = list(gps_collection.find({}, {"_id": 0}))
    return gps_data

# ✅ Calendar Routes
@app.post("/calendar/")
async def add_event(event: CalendarEvent, token: str = Depends(verify_token)):
    calendar_collection.insert_one(event.dict())
    return {"message": "Event added to calendar"}

@app.get("/calendar/")
async def get_calendar(token: str = Depends(verify_token)):
    events = list(calendar_collection.find({}, {"_id": 0}))
    return events

# ✅ Protected Test Route
@app.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    return {"message": "You have access to this route"}

# ✅ Start the server (Render-compatible)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

