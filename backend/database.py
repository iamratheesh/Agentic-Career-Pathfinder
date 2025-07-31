
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from config import settings

client: AsyncIOMotorClient = None

async def connect_to_mongodb():
    """Establishes a connection to MongoDB."""
    global client
    try:
        client = AsyncIOMotorClient(
            settings.MONGO_URI,
            connectTimeoutMS=10000,
            serverSelectionTimeoutMS=10000
        )
        await client.admin.command('ping')
        print("MongoDB connection established successfully.")
    except (ConnectionFailure, OperationFailure) as e:
        print(f"MongoDB connection failed: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during MongoDB connection: {e}")
        raise

async def close_mongodb_connection():
    """Closes the MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")

def get_database():
    """Returns the database instance."""
    if client:
        return client[settings.DB_NAME]
    raise ConnectionError("MongoDB client is not initialized.")