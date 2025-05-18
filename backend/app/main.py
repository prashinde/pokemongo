from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager
from app.core.config import settings
from app.models.pokemon import Pokemon, PokemonSpawn
from app.models.user import User
from app.api.routes import auth, pokemon, pokedex
from app.services.spawn_manager import spawn_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=client[settings.DB_NAME],
        document_models=[User, Pokemon, PokemonSpawn]
    )
    
    # Start spawn manager
    await spawn_manager.start()
    print("Pokemon Spawn Manager initialized")
    
    yield
    
    # Cleanup
    await spawn_manager.cleanup()
    client.close()

app = FastAPI(
    title="Pokemon GO Clone API",
    description="Backend API for Pokemon GO Clone",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(pokemon.router, prefix="/api/pokemon", tags=["Pokemon"])
app.include_router(pokedex.router, prefix="/api/pokedex", tags=["Pokedex"])

@app.get("/")
async def root():
    return {"message": "Welcome to Pokemon GO Clone API"} 