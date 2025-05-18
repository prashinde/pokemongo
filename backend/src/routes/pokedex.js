const express = require('express');
const router = express.Router();
const Pokedex = require('../models/Pokedex');
const User = require('../models/User');
const jwt = require('jsonwebtoken');

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

// Get user's Pokedex
router.get('/', auth, async (req, res) => {
  try {
    const pokedex = await Pokedex.find({ user: req.user._id })
      .populate('pokemon')
      .sort({ caughtAt: -1 });

    res.json(pokedex);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching Pokedex', error: error.message });
  }
});

// Get specific Pokemon details from user's Pokedex
router.get('/:pokemonId', auth, async (req, res) => {
  try {
    const entry = await Pokedex.findOne({
      user: req.user._id,
      pokemon: req.params.pokemonId
    }).populate('pokemon');

    if (!entry) {
      return res.status(404).json({ message: 'Pokemon not found in Pokedex' });
    }

    res.json(entry);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching Pokemon details', error: error.message });
  }
});

module.exports = router;
