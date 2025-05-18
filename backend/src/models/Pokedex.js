const mongoose = require('mongoose');

const pokedexSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  pokemon: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Pokemon',
    required: true
  },
  caughtAt: {
    type: Date,
    default: Date.now
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
  count: {
    type: Number,
    default: 1
  }
});

// Compound index to ensure unique pokemon per user
pokedexSchema.index({ user: 1, pokemon: 1 }, { unique: true });

module.exports = mongoose.model('Pokedex', pokedexSchema);
