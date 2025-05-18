from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app.core.config import settings
from app.models.user import User, UserCreate, UserLogin

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    logger.debug(f"Verifying password (plain_password length: {len(plain_password)})")
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    logger.debug(f"Hashing password (length: {len(password)})")
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await User.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    logger.debug(f"Registration attempt for email: {user_data.email}")
    
    # Check if user already exists
    existing_user = await User.find_one({"email": user_data.email})
    if existing_user:
        logger.warning(f"Registration failed: Email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    logger.debug("Creating new user")
    try:
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password)
        )
        logger.debug("User object created, attempting to insert into database")
        
        await user.insert()
        logger.debug("User inserted successfully")
        
        # Create access token
        access_token = create_access_token({"sub": user.email})
        logger.debug("Access token created successfully")
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "username": current_user.username,
        "last_location": current_user.last_location
    } 