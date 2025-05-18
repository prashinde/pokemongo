from datetime import datetime, timedelta
import asyncio
from typing import List
import random
from geopy.distance import geodesic
from app.models.pokemon import Pokemon, PokemonSpawn
from app.core.config import settings

class SpawnManager:
    def __init__(self):
        self._running = False
        self._task = None
        
    async def start(self):
        """Start the spawn manager."""
        if self._running:
            return
            
        self._running = True
        await self.cleanup_expired_spawns()
        self._task = asyncio.create_task(self._spawn_loop())
        
    async def cleanup(self):
        """Cleanup the spawn manager."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
                
    async def cleanup_expired_spawns(self):
        """Remove expired spawns from the database."""
        await PokemonSpawn.find(
            {"despawn_time": {"$lt": datetime.utcnow()}}
        ).delete()
        
    async def get_nearby_spawns(self, lat: float, lng: float, radius_meters: float = None) -> List[PokemonSpawn]:
        """Get nearby Pokemon spawns within radius."""
        if radius_meters is None:
            radius_meters = settings.SPAWN_RADIUS_METERS
            
        current_location = (lat, lng)
        all_active_spawns = await PokemonSpawn.find(
            {"despawn_time": {"$gt": datetime.utcnow()}}
        ).to_list()
        
        nearby_spawns = []
        for spawn in all_active_spawns:
            spawn_location = (spawn.location["lat"], spawn.location["lng"])
            distance = geodesic(current_location, spawn_location).meters
            if distance <= radius_meters:
                nearby_spawns.append(spawn)
                
        return nearby_spawns
        
    async def _spawn_loop(self):
        """Main spawn loop that periodically spawns new Pokemon."""
        while self._running:
            try:
                await self._generate_spawns()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Error in spawn loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _generate_spawns(self):
        """Generate new Pokemon spawns if needed."""
        current_spawns = await PokemonSpawn.find(
            {"despawn_time": {"$gt": datetime.utcnow()}}
        ).count()
        
        if current_spawns >= settings.MAX_ACTIVE_SPAWNS:
            return
            
        num_to_spawn = settings.MAX_ACTIVE_SPAWNS - current_spawns
        all_pokemon = await Pokemon.find().to_list()
        
        if not all_pokemon:
            print("No Pokemon available in database. Skipping spawn generation.")
            return
            
        for _ in range(num_to_spawn):
            pokemon = random.choice(all_pokemon)
            # TODO: Implement proper location generation strategy
            spawn_location = {
                "lat": random.uniform(-90, 90),
                "lng": random.uniform(-180, 180)
            }
            
            spawn = PokemonSpawn(
                pokemon_id=pokemon.pokemon_id,
                location=spawn_location,
                spawn_time=datetime.utcnow(),
                despawn_time=datetime.utcnow() + timedelta(minutes=settings.SPAWN_DURATION_MINUTES)
            )
            await spawn.insert()

spawn_manager = SpawnManager() 