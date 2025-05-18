from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models.user import User
from app.models.pokemon import Pokemon, PokemonSpawn
from app.api.routes.auth import get_current_user

router = APIRouter()

@router.get("/pokemon", response_model=List[dict])
async def get_all_pokemon():
    """Get all Pokemon in the database."""
    pokemon_list = await Pokemon.find_all().to_list()
    return [
        {
            "pokemon_id": p.pokemon_id,
            "name": p.name,
            "types": p.types,
            "base_stats": p.base_stats,
            "catch_rate": p.catch_rate,
            "spawn_rate": p.spawn_rate,
            "image_url": p.image_url
        }
        for p in pokemon_list
    ]

@router.get("/pokemon/{pokemon_id}", response_model=dict)
async def get_pokemon(pokemon_id: int):
    """Get details for a specific Pokemon."""
    pokemon = await Pokemon.find_one({"pokemon_id": pokemon_id})
    if not pokemon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pokemon not found"
        )
        
    return {
        "pokemon_id": pokemon.pokemon_id,
        "name": pokemon.name,
        "types": pokemon.types,
        "base_stats": pokemon.base_stats,
        "catch_rate": pokemon.catch_rate,
        "spawn_rate": pokemon.spawn_rate,
        "image_url": pokemon.image_url
    }

@router.get("/caught", response_model=List[dict])
async def get_caught_pokemon(current_user: User = Depends(get_current_user)):
    """Get all Pokemon caught by the current user."""
    caught_spawns = await PokemonSpawn.find(
        {"caught_by": str(current_user.id)}
    ).to_list()
    
    result = []
    for spawn in caught_spawns:
        pokemon = await Pokemon.find_one({"pokemon_id": spawn.pokemon_id})
        if pokemon:
            result.append({
                "pokemon_id": pokemon.pokemon_id,
                "name": pokemon.name,
                "types": pokemon.types,
                "image_url": pokemon.image_url,
                "caught_at": spawn.spawn_time
            })
            
    return result

@router.post("/pokemon", response_model=dict)
async def create_pokemon(pokemon_data: dict):
    """Create a new Pokemon."""
    # Check if Pokemon already exists
    existing = await Pokemon.find_one({"pokemon_id": pokemon_data["pokemon_id"]})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pokemon with ID {pokemon_data['pokemon_id']} already exists"
        )
    
    pokemon = Pokemon(**pokemon_data)
    await pokemon.insert()
    return {
        "pokemon_id": pokemon.pokemon_id,
        "name": pokemon.name,
        "types": pokemon.types,
        "base_stats": pokemon.base_stats,
        "catch_rate": pokemon.catch_rate,
        "spawn_rate": pokemon.spawn_rate,
        "image_url": pokemon.image_url
    } 