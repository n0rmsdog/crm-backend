from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import MongoClient
from pydantic import BaseModel
import os

# Initialize FastAPI app
app = FastAPI()

# Load MongoDB connection string from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://n0rms:2m6dUSyTbwvfpbFq@cluster0.nf19p.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true")
client = MongoClient(MONGO_URI)
db = client["crm_backend"]

# OAuth2 authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dummy user database (replace with real user authentication later)
fake_users_db = {
    "admin": {
        "username": "norms",
        "password": "crm",
        "role": "admin"
    }
}

# Pydantic model for customer data
class Customer(BaseModel):
    name: str
    email: str

# Home route
@app.get("/")
def home():
    return {"message": "Welcome to the CRM API!"}

# Token endpoint for authentication
@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": form_data.username, "token_type": "bearer"}

# Protected route to list customers (requires authentication)
@app.get("/customers/")
async def list_customers(token: str = Depends(oauth2_scheme)):
    customers = list(db.customers.find({}, {"_id": 0}))
    return customers

# Protected route to add a new customer
@app.post("/customers/")
async def add_customer(customer: Customer, token: str = Depends(oauth2_scheme)):
    db.customers.insert_one(customer.dict())
    return {"message": "Customer added successfully"}

