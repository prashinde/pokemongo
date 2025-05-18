const mongoose = require('mongoose');

const pokemonSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  number: {
    type: Number,
    required: true,
    unique: true
  },
  type: [{
    type: String,
    required: true
  }],
  stats: {
    hp: Number,
    attack: Number,
    defense: Number,
    speed: Number
  },
  image: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
});

module.exports = mongoose.model('Pokemon', pokemonSchema);
