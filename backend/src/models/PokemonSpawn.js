const mongoose = require('mongoose');

const pokemonSpawnSchema = new mongoose.Schema({
  pokemon: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Pokemon',
    required: true
  },
  location: {
    type: {
      type: String,
      enum: ['Point'],
      default: 'Point'
    },
    coordinates: {
      type: [Number], // [longitude, latitude]
      required: true
    }
  },
  spawnedAt: {
    type: Date,
    default: Date.now
  },
  despawnAt: {
    type: Date,
    required: true
  },
  maxCaptures: {
    type: Number,
    required: true,
    default: 10
  },
  currentCaptures: {
    type: Number,
    default: 0
  },
  capturedBy: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }]
});

// Index for geospatial queries
pokemonSpawnSchema.index({ location: '2dsphere' });

// Index for finding active spawns
pokemonSpawnSchema.index({ despawnAt: 1 });

// Virtual property to check if spawn is still active
pokemonSpawnSchema.virtual('isActive').get(function() {
  return this.despawnAt > new Date() && this.currentCaptures < this.maxCaptures;
});

module.exports = mongoose.model('PokemonSpawn', pokemonSpawnSchema);
