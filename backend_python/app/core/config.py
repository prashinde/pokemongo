from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URI: str = "mongodb+srv://pratikchshinde:Gauri%40123@cluster0.jxbviag.mongodb.net/pokemon-go-clone?retryWrites=true&w=majority&appName=Cluster0&replicaSet=atlas-oiqbf0-shard-0"
    DB_NAME: str = "pokemon-go-clone"
    
    # JWT settings
    SECRET_KEY: str = "your_super_secret_jwt_key_for_pokemon_go_clone"  # Using the same JWT secret as JS backend
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Pokemon spawn settings
    SPAWN_RADIUS_METERS: float = 100.0
    MAX_ACTIVE_SPAWNS: int = 10
    SPAWN_DURATION_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings() 