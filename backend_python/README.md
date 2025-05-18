# Pokemon GO Clone Backend (Python)

This is the Python backend for the Pokemon GO Clone application, built with FastAPI and MongoDB.

## Setup

1. Create a `.env` file in the `backend_python` directory with the following content:

```
MONGODB_URI=your_mongodb_uri
DB_NAME=pokemon_go_clone
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:3000
SPAWN_RADIUS_METERS=100.0
MAX_ACTIVE_SPAWNS=10
SPAWN_DURATION_MINUTES=30
```

2. Run the server:

```bash
./start.sh
```

The server will start on http://localhost:5000 with the API documentation available at http://localhost:5000/docs

## API Endpoints

### Authentication

- POST `/api/auth/register` - Register a new user
- POST `/api/auth/token` - Login and get access token
- GET `/api/auth/me` - Get current user info

### Pokemon

- GET `/api/pokemon/nearby` - Get nearby Pokemon spawns
- POST `/api/pokemon/catch/{spawn_id}` - Attempt to catch a Pokemon

### Pokedex

- GET `/api/pokedex/pokemon` - Get all Pokemon
- GET `/api/pokedex/pokemon/{pokemon_id}` - Get specific Pokemon details
- GET `/api/pokedex/caught` - Get user's caught Pokemon

## Development

The server uses:

- FastAPI for the web framework
- Beanie/Motor for MongoDB ODM
- JWT for authentication
- Geopy for location calculations

Hot reload is enabled by default, so any changes to the code will automatically restart the server.
