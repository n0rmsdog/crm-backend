import os
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from pydantic import BaseModel
import certifi  # ✅ Fix SSL issues with MongoDB

# ✅ Force Render to Use Environment Port
PORT = int(os.getenv("PORT", 8000))  # Render assigns a PORT dynamically

# ✅ MongoDB Connection (Render)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())  # ✅ Fix TLS issue
db = client["crm_backend"]

# ✅ Collections
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

# ✅ Dummy User Database (Replace with real authentication)
fake_users_db = {"admin": {"username": "norms", "password": "crm", "role": "admin"}}

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

# ----------------- ✅ ROUTES -----------------
@app.get("/")
def home():
    return {"message": "Welcome to the CRM API!"}

@app.get("/customers/")
async def get_customers(token: dict = Depends(verify_token)):
    customers = list(customers_collection.find({}, {"_id": 0}))
    return customers

@app.post("/customers/")
async def create_customer(customer: BaseModel, token: dict = Depends(verify_token)):
    customers_collection.insert_one(customer.dict())
    return {"message": "Customer added successfully"}

# ✅ Add similar routes for jobs, invoices, etc.

# ✅ Run FastAPI on Render's Assigned Port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
