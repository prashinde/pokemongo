const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const spawnManager = require('./services/SpawnManager');

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection
const connectDB = async () => {
  try {
    if (!process.env.MONGODB_URI) {
      throw new Error('MONGODB_URI is not defined in environment variables');
    }

    const conn = await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      retryWrites: true,
      w: 'majority',
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    });

    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};

// Handle MongoDB connection events
mongoose.connection.on('connected', () => {
  console.log('Mongoose connected to MongoDB');
});

mongoose.connection.on('error', (err) => {
  console.error('Mongoose connection error:', err);
});

mongoose.connection.on('disconnected', () => {
  console.log('Mongoose disconnected');
});

// Connect to MongoDB before starting the server
connectDB().then(async () => {
  // Initialize spawn manager
  await spawnManager.start();
  console.log('Pokemon Spawn Manager initialized');

  // Root route
  app.get('/', (req, res) => {
    res.json({ message: 'Welcome to Pokemon GO Clone API' });
  });

  // Test route
  app.get('/api/test', (req, res) => {
    res.json({ message: 'API is working!' });
  });

  // Routes
  app.use('/api/auth', require('./routes/auth'));
  app.use('/api/pokemon', require('./routes/pokemon'));
  app.use('/api/pokedex', require('./routes/pokedex'));

  // Enhanced error handling
  app.use((err, req, res, next) => {
    console.error('Error:', err);
    
    if (err.name === 'ValidationError') {
      return res.status(400).json({ 
        message: 'Validation Error', 
        errors: Object.values(err.errors).map(e => e.message) 
      });
    }
    
    if (err.name === 'MongoError' || err.name === 'MongoServerError') {
      return res.status(503).json({ 
        message: 'Database Error', 
        error: err.message 
      });
    }
    
    res.status(500).json({ 
      message: 'Internal Server Error',
      error: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong!'
    });
  });

  const PORT = process.env.PORT || 5000;
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });
});

// Handle process termination
process.on('SIGINT', async () => {
  try {
    await mongoose.connection.close();
    console.log('Mongoose connection closed through app termination');
    process.exit(0);
  } catch (err) {
    console.error('Error during shutdown:', err);
    process.exit(1);
  }
});
