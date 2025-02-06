from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

app = FastAPI()
@app.get("/")
def home():
    return {"message": "Welcome to the CRM API!"}
# Database Connection
client = MongoClient("mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["crm_backend"]

# Collections
users_collection = db["users"]
customers_collection = db["customers"]
jobs_collection = db["jobs"]

# JWT Secret Key
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User Model
class User(BaseModel):
    username: str
    password: str

# Token Model
class Token(BaseModel):
    access_token: str
    token_type: str

# Pydantic Models
class Customer(BaseModel):
    name: str
    email: str

class Job(BaseModel):
    customer_email: str
    description: str
    assigned_to: Optional[str] = None
    status: str = "Pending"
    due_date: Optional[datetime] = None
    completion_notes: Optional[str] = None

# Helper Functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username})
    if not user or not verify_password(password, user["password"]):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = users_collection.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# API Routes

## Authentication
@app.post("/register/")
def register_user(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "User registered successfully"}

@app.post("/token/", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

## Customers
@app.post("/customers/")
def create_customer(customer: Customer, current_user: dict = Depends(get_current_user)):
    if customers_collection.find_one({"email": customer.email}):
        raise HTTPException(status_code=400, detail="Customer already exists")
    
    customers_collection.insert_one(customer.dict())
    return {"message": "Customer added successfully"}

@app.get("/customers/", response_model=List[Customer])
def list_customers(current_user: dict = Depends(get_current_user)):
    return list(customers_collection.find({}, {"_id": 0}))

@app.delete("/customers/{email}")
def delete_customer(email: str, current_user: dict = Depends(get_current_user)):
    result = customers_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {"message": "Customer deleted successfully"}

## Jobs
@app.post("/jobs/")
def create_job(job: Job, current_user: dict = Depends(get_current_user)):
    job_dict = job.dict()
    job_dict["created_at"] = datetime.utcnow()
    
    jobs_collection.insert_one(job_dict)
    return {"message": "Job added successfully"}

@app.get("/jobs/", response_model=List[Job])
def list_jobs(current_user: dict = Depends(get_current_user)):
    return list(jobs_collection.find({}, {"_id": 0}))

@app.get("/jobs/assigned/{email}", response_model=List[Job])
def list_assigned_jobs(email: str, current_user: dict = Depends(get_current_user)):
    return list(jobs_collection.find({"assigned_to": email}, {"_id": 0}))

@app.put("/jobs/complete/{email}")
def complete_job(email: str, notes: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    result = jobs_collection.update_one(
        {"customer_email": email, "status": "Pending"},
        {"$set": {"status": "Completed", "completed_at": datetime.utcnow(), "completion_notes": notes}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="No pending job found for this customer")

    return {"message": "Job marked as completed"}

@app.get("/jobs/notes/{email}")
def view_notes(email: str, current_user: dict = Depends(get_current_user)):
    job = jobs_collection.find_one({"customer_email": email})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"completion_notes": job.get("completion_notes", "No notes available")}

@app.delete("/jobs/{email}")
def delete_job(email: str, current_user: dict = Depends(get_current_user)):
    result = jobs_collection.delete_one({"customer_email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}

# Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "password123":
        return {"access_token": "your_generated_token_here", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

