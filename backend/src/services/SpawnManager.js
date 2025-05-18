const Pokemon = require('../models/Pokemon');
const PokemonSpawn = require('../models/PokemonSpawn');

class SpawnManager {
  constructor() {
    this.spawnInterval = 5 * 60 * 1000; // 5 minutes
    this.despawnTime = 30 * 60 * 1000;  // 30 minutes
    this.maxSpawnsPerArea = 10;
    this.spawnRadius = 100; // meters
  }

  // Generate random coordinates within radius of a point
  generateRandomPoint(centerLat, centerLng, radius) {
    const r = radius / 111300; // convert meters to degrees
    const u = Math.random();
    const v = Math.random();
    const w = r * Math.sqrt(u);
    const t = 2 * Math.PI * v;
    const x = w * Math.cos(t);
    const y = w * Math.sin(t);

    return {
      latitude: centerLat + y,
      longitude: centerLng + x * Math.cos(centerLat)
    };
  }

  // Spawn Pokemon in an area
  async spawnPokemon(latitude, longitude) {
    try {
      // Check existing spawns in the area
      const existingSpawns = await PokemonSpawn.find({
        location: {
          $near: {
            $geometry: {
              type: 'Point',
              coordinates: [longitude, latitude]
            },
            $maxDistance: this.spawnRadius
          }
        },
        despawnAt: { $gt: new Date() }
      });

      if (existingSpawns.length >= this.maxSpawnsPerArea) {
        return null;
      }

      // Get random Pokemon
      const pokemonCount = await Pokemon.countDocuments();
      const random = Math.floor(Math.random() * pokemonCount);
      const randomPokemon = await Pokemon.findOne().skip(random);

      if (!randomPokemon) {
        throw new Error('No Pokemon found in database');
      }

      // Generate spawn point
      const spawnPoint = this.generateRandomPoint(latitude, longitude, this.spawnRadius);

      // Create spawn
      const spawn = new PokemonSpawn({
        pokemon: randomPokemon._id,
        location: {
          type: 'Point',
          coordinates: [spawnPoint.longitude, spawnPoint.latitude]
        },
        despawnAt: new Date(Date.now() + this.despawnTime),
        maxCaptures: Math.floor(Math.random() * 5) + 5 // 5-10 captures
      });

      await spawn.save();
      return spawn;
    } catch (error) {
      console.error('Error spawning Pokemon:', error);
      return null;
    }
  }

  // Clean up expired spawns
  async cleanupExpiredSpawns() {
    try {
      await PokemonSpawn.deleteMany({
        $or: [
          { despawnAt: { $lt: new Date() } },
          { currentCaptures: { $gte: mongoose.expr('$maxCaptures') } }
        ]
      });
    } catch (error) {
      console.error('Error cleaning up spawns:', error);
    }
  }

  // Start spawn manager
  async start() {
    // Clean up expired spawns on startup
    await this.cleanupExpiredSpawns();

    // Set up periodic cleanup
    setInterval(() => {
      this.cleanupExpiredSpawns();
    }, this.spawnInterval);
  }
}

module.exports = new SpawnManager(); 