from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from beanie import init_beanie
from app.models.pokemon import Pokemon
from app.core.config import settings

# Initial Pokemon data
INITIAL_POKEMON = [
    {
        "pokemon_id": 1,
        "name": "Bulbasaur",
        "types": ["Grass", "Poison"],
        "base_stats": {
            "hp": 45,
            "attack": 49,
            "defense": 49,
            "special-attack": 65,
            "special-defense": 65,
            "speed": 45
        },
        "catch_rate": 0.2,
        "spawn_rate": 0.1,
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png"
    },
    {
        "pokemon_id": 4,
        "name": "Charmander",
        "types": ["Fire"],
        "base_stats": {
            "hp": 39,
            "attack": 52,
            "defense": 43,
            "special-attack": 60,
            "special-defense": 50,
            "speed": 65
        },
        "catch_rate": 0.2,
        "spawn_rate": 0.1,
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png"
    },
    {
        "pokemon_id": 7,
        "name": "Squirtle",
        "types": ["Water"],
        "base_stats": {
            "hp": 44,
            "attack": 48,
            "defense": 65,
            "special-attack": 50,
            "special-defense": 64,
            "speed": 43
        },
        "catch_rate": 0.2,
        "spawn_rate": 0.1,
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png"
    },
    {
        "pokemon_id": 25,
        "name": "Pikachu",
        "types": ["Electric"],
        "base_stats": {
            "hp": 35,
            "attack": 55,
            "defense": 40,
            "special-attack": 50,
            "special-defense": 50,
            "speed": 90
        },
        "catch_rate": 0.2,
        "spawn_rate": 0.1,
        "image_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
    }
]

async def init_db():
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[Pokemon]
    )
    
    # Clear existing Pokemon
    await Pokemon.delete_all()
    
    # Insert initial Pokemon
    for pokemon_data in INITIAL_POKEMON:
        pokemon = Pokemon(**pokemon_data)
        await pokemon.insert()
    
    print("Pokemon initialized successfully!")
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    asyncio.run(init_db()) 