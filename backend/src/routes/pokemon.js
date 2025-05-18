const express = require('express');
const router = express.Router();
const Pokemon = require('../models/Pokemon');
const PokemonSpawn = require('../models/PokemonSpawn');
const User = require('../models/User');
const jwt = require('jsonwebtoken');
const spawnManager = require('../services/SpawnManager');

// Performance monitoring middleware
const performanceMonitor = (req, res, next) => {
  const start = process.hrtime();
  
  // Override res.json to measure response time
  const originalJson = res.json;
  res.json = function(body) {
    const diff = process.hrtime(start);
    const time = diff[0] * 1e3 + diff[1] * 1e-6; // Convert to milliseconds
    console.log(`[Backend Performance] ${req.method} ${req.originalUrl} - ${time.toFixed(2)}ms`);
    console.log('[Backend Query Parameters]:', req.query);
    console.log('[Backend Response Size]:', JSON.stringify(body).length, 'bytes');
    return originalJson.call(this, body);
  };
  
  next();
};

// Apply performance monitoring to all routes
router.use(performanceMonitor);

// Middleware to verify JWT token
const auth = async (req, res, next) => {
  try {
    const token = req.header('Authorization').replace('Bearer ', '');
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findOne({ _id: decoded.userId });
    
    if (!user) {
      throw new Error();
    }

    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ message: 'Please authenticate' });
  }
};

// Get nearby Pokemon spawns
router.get('/nearby', auth, async (req, res) => {
  try {
    const { longitude, latitude } = req.query;
    const coords = [parseFloat(longitude), parseFloat(latitude)];

    // Attempt to spawn new Pokemon
    await spawnManager.spawnPokemon(parseFloat(latitude), parseFloat(longitude));
    
    const nearbySpawns = await PokemonSpawn.find({
      location: {
        $near: {
          $geometry: {
            type: 'Point',
            coordinates: coords
          },
          $maxDistance: 100 // 100 meters radius
        }
      },
      despawnAt: { $gt: new Date() },
      currentCaptures: { $lt: mongoose.expr('$maxCaptures') }
    }).populate('pokemon');

    res.json(nearbySpawns);
  } catch (error) {
    res.status(500).json({ message: 'Error finding nearby Pokemon', error: error.message });
  }
});

// Attempt to catch a Pokemon
router.post('/catch/:spawnId', auth, async (req, res) => {
  try {
    const { longitude, latitude } = req.body;
    const spawn = await PokemonSpawn.findById(req.params.spawnId).populate('pokemon');

    if (!spawn) {
      return res.status(404).json({ message: 'Pokemon spawn not found' });
    }

    if (!spawn.isActive) {
      return res.status(400).json({ message: 'This Pokemon is no longer available' });
    }

    // Check if user is within range (10 meters)
    const distance = getDistance(
      [parseFloat(longitude), parseFloat(latitude)],
      spawn.location.coordinates
    );

    if (distance > 10) {
      return res.status(400).json({ message: 'You are too far from this Pokemon' });
    }

    // Check if user already caught this spawn
    if (spawn.capturedBy.includes(req.user._id)) {
      return res.status(400).json({ message: 'You already caught this Pokemon' });
    }

    // Update spawn and user atomically
    spawn.currentCaptures += 1;
    spawn.capturedBy.push(req.user._id);
    await spawn.save();

    // Add to user's pokedex
    req.user.pokedex.push(spawn.pokemon);
    await req.user.save();

    res.json({ message: 'Pokemon caught successfully!', pokemon: spawn.pokemon });
  } catch (error) {
    res.status(500).json({ message: 'Error catching Pokemon', error: error.message });
  }
});

// Helper function to calculate distance between coordinates in meters
function getDistance(coords1, coords2) {
  const R = 6371e3; // Earth's radius in meters
  const φ1 = coords1[1] * Math.PI/180;
  const φ2 = coords2[1] * Math.PI/180;
  const Δφ = (coords2[1]-coords1[1]) * Math.PI/180;
  const Δλ = (coords2[0]-coords1[0]) * Math.PI/180;

  const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
          Math.cos(φ1) * Math.cos(φ2) *
          Math.sin(Δλ/2) * Math.sin(Δλ/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

  return R * c;
}

module.exports = router;
