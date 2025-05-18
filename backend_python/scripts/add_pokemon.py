import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.pokemon import Pokemon
from app.core.config import settings
from tests.data.pokemon_data import TEST_POKEMON

async def add_pokemon():
    """Add initial Pokemon to the database."""
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[Pokemon]
    )
    
    # Clear existing Pokemon
    await Pokemon.delete_all()
    
    # Insert Pokemon
    for pokemon_data in TEST_POKEMON:
        pokemon = Pokemon(**pokemon_data)
        await pokemon.insert()
        print(f"Added {pokemon.name} to database")
    
    print("\nAll Pokemon added successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(add_pokemon()) 