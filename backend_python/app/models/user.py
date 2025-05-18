from beanie import Document
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
        
    async def insert(self, *args, **kwargs):
        logger.debug(f"Inserting new user: {self.email}")
        try:
            result = await super().insert(*args, **kwargs)
            logger.debug(f"User inserted successfully: {self.email}")
            return result
        except Exception as e:
            logger.error(f"Error inserting user {self.email}: {str(e)}")
            raise
    
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