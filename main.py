from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
import uvicorn
from pymongo import MongoClient
from pydantic import BaseModel

# ----------------- Constants -----------------
SECRET_KEY = "G1-WlvEmko2Q0oG7H6wIOWUwBx_r0P_gUX8Q5VnrcOU"
ALGORITHM = "HS256"

# ----------------- Initialize FastAPI -----------------
app = FastAPI()

# ----------------- MongoDB Connection -----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["crm_database"]
customers_collection = db["customers"]

# ----------------- OAuth2 Token Authentication -----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ----------------- Authentication Functions -----------------
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
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ----------------- Models -----------------
class Customer(BaseModel):
    name: str
    email: str


# ----------------- API Routes -----------------
@app.post("/token")
async def login():
    """Generate and return a permanent JWT token."""
    token = create_access_token({"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/customers/")
async def create_customer(customer: Customer, token: str = Depends(verify_token)):
    """Add a new customer to MongoDB."""
    customers_collection.insert_one(customer.dict())
    return {"message": "Customer added successfully"}


@app.get("/customers/")
async def get_customers(token: str = Depends(verify_token)):
    """Retrieve all customers from MongoDB."""
    customers = list(customers_collection.find({}, {"_id": 0}))  # Exclude MongoDB _id field
    return customers


@app.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    """Protected route requiring authentication."""
    return {"message": "You have access to this route"}


# ----------------- Ensure PORT Works for Render -----------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)

