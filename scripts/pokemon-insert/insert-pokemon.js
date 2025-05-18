import { MongoClient } from 'mongodb';
import { POKEMON_DATA } from './pokemon-data.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// MongoDB Atlas connection string should be in .env file
const uri = process.env.MONGODB_URI;

if (!uri) {
    console.error('Please provide MONGODB_URI in .env file');
    process.exit(1);
}

async function insertPokemon() {
    const client = new MongoClient(uri);
    
    try {
        await client.connect();
        console.log('Connected to MongoDB Atlas');
        
        const database = client.db('pokemon-go-clone');
        const collection = database.collection('pokemon');
        
        // Insert or update Pokemon data using bulkWrite
        const bulkOps = POKEMON_DATA.map(pokemon => ({
            updateOne: {
                filter: { pokemon_id: pokemon.pokemon_id },
                update: { $set: pokemon },
                upsert: true
            }
        }));
        
        const result = await collection.bulkWrite(bulkOps);
        console.log(`Successfully upserted Pokemon data:
        - Inserted: ${result.upsertedCount}
        - Modified: ${result.modifiedCount}
        - Total Pokemon in database: ${await collection.countDocuments()}`);
        
    } catch (error) {
        console.error('Error:', error);
    } finally {
        await client.close();
        console.log('Disconnected from MongoDB Atlas');
    }
}

// Run the insertion
insertPokemon(); 