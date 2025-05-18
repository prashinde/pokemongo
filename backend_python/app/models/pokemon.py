from beanie import Document
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class Pokemon(Document):
    pokemon_id: int
    name: str
    types: List[str]
    base_stats: Dict[str, int]  # {hp: int, attack: int, defense: int, etc.}
    catch_rate: float
    spawn_rate: float
    image_url: str
    
    class Settings:
        name = "pokemon"

class PokemonSpawn(Document):
    pokemon_id: int
    location: Dict[str, float]  # {lat: float, lng: float}
    spawn_time: datetime = datetime.utcnow()
    despawn_time: datetime
    caught_by: Optional[str] = None  # User ID who caught this spawn
    
    class Settings:
        name = "pokemon_spawns"
        
    model_config = {
        "json_schema_extra": {
            "example": {
                "pokemon_id": 25,  # Pikachu
                "location": {"lat": 40.7128, "lng": -74.0060},
                "spawn_time": "2024-03-14T12:00:00",
                "despawn_time": "2024-03-14T12:30:00"
            }
        }
    } 