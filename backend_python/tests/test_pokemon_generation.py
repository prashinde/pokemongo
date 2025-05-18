import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.pokemon import Pokemon
from app.core.config import settings
from tests.data.pokemon_data import TEST_POKEMON

@pytest.fixture
async def setup_database():
    """Setup test database connection."""
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[Pokemon]
    )
    yield client
    # Cleanup
    await Pokemon.delete_all()
    client.close()

@pytest.mark.asyncio
async def test_pokemon_generation(setup_database):
    """Test generating Pokemon in the database."""
    # Clear any existing Pokemon
    await Pokemon.delete_all()
    
    # Insert test Pokemon
    for pokemon_data in TEST_POKEMON:
        pokemon = Pokemon(**pokemon_data)
        await pokemon.insert()
    
    # Verify Pokemon were inserted
    all_pokemon = await Pokemon.find().to_list()
    assert len(all_pokemon) == len(TEST_POKEMON)
    
    # Verify specific Pokemon
    bulbasaur = await Pokemon.find_one({"pokemon_id": 1})
    assert bulbasaur is not None
    assert bulbasaur.name == "Bulbasaur"
    assert "Grass" in bulbasaur.types
    
    # Verify Pikachu stats
    pikachu = await Pokemon.find_one({"pokemon_id": 25})
    assert pikachu is not None
    assert pikachu.base_stats["speed"] == 90
    assert pikachu.types == ["Electric"]

if __name__ == "__main__":
    asyncio.run(test_pokemon_generation(None)) 