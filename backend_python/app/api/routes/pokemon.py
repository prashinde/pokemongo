from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.user import User
from app.models.pokemon import Pokemon, PokemonSpawn
from app.services.spawn_manager import spawn_manager
from app.api.routes.auth import get_current_user

router = APIRouter()

@router.get("/nearby")
async def get_nearby_pokemon(
    lat: float,
    lng: float,
    radius: Optional[float] = None,
    current_user: User = Depends(get_current_user)
):
    """Get nearby Pokemon spawns."""
    # Update user's last location
    current_user.last_location = {"lat": lat, "lng": lng}
    await current_user.save()
    
    # Get nearby spawns
    spawns = await spawn_manager.get_nearby_spawns(lat, lng, radius)
    
    # Fetch Pokemon details for each spawn
    result = []
    for spawn in spawns:
        pokemon = await Pokemon.find_one({"pokemon_id": spawn.pokemon_id})
        if pokemon:
            result.append({
                "spawn_id": str(spawn.id),
                "pokemon_id": pokemon.pokemon_id,
                "name": pokemon.name,
                "types": pokemon.types,
                "image_url": pokemon.image_url,
                "location": spawn.location,
                "despawn_time": spawn.despawn_time,
                "caught": spawn.caught_by is not None
            })
    
    return result

@router.post("/catch/{spawn_id}")
async def catch_pokemon(
    spawn_id: str,
    current_user: User = Depends(get_current_user)
):
    """Attempt to catch a Pokemon."""
    # Find the spawn
    spawn = await PokemonSpawn.get(spawn_id)
    if not spawn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pokemon spawn not found"
        )
        
    # Check if Pokemon is already caught
    if spawn.caught_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Pokemon has already been caught"
        )
        
    # Check if Pokemon has despawned
    if spawn.despawn_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Pokemon has despawned"
        )
        
    # Get Pokemon details
    pokemon = await Pokemon.find_one({"pokemon_id": spawn.pokemon_id})
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pokemon details not found"
        )
        
    # TODO: Implement catch rate mechanics
    # For now, always successful
    spawn.caught_by = str(current_user.id)
    await spawn.save()
    
    return {
        "success": True,
        "message": f"Successfully caught {pokemon.name}!",
        "pokemon": {
            "id": pokemon.pokemon_id,
            "name": pokemon.name,
            "types": pokemon.types,
            "image_url": pokemon.image_url
        }
    } 