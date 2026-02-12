from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

app = FastAPI()

security = HTTPBearer()

# Load the .env into the environment
load_dotenv()

# Your secret - in production use environment variable
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
 
# Login Request Model
class LoginRequest(BaseModel):
    username: str
    password: str

# Create JWT
def create_token(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24) # Expires in 24 hours
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Verify JWT
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
# Login Endpoint -> To test the JWT token
@app.post('/login')
def login(request: LoginRequest):
    
    # Dummy check with local values
    if request.username == "admin" and request.password == "password":
        token = create_token(user_id=1)
        return {
            "access_token": token,
            "token_type": "bearer",
        }
    raise HTTPException(status_code=401, detail="Wrong Credentials")

# protected Endpoint
@app.get('/protected')
def protected_route(payload: dict = Depends(verify_token)):
    return {
        "message": f"Hello user {payload['user_id']}!"
    }

@app.get('/')
def homw_page():
    return {
        "health": "All good!!"
    }