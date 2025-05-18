from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(Document, UserBase):
    hashed_password: str
    created_at: datetime = datetime.utcnow()
    last_location: Optional[Dict[str, float]] = None  # {lat: float, lng: float}
    
    class Settings:
        name = "users"
        
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "trainer@example.com",
                "username": "AshKetchum",
                "hashed_password": "hashedpassword123",
                "last_location": {"lat": 40.7128, "lng": -74.0060}
            }
        }
    } 