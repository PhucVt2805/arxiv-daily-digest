import os
from beanie import init_beanie
from qdrant_client import AsyncQdrantClient
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client.models import Distance, VectorParams

from src.utils.log_config import get_logger
from src.model import ArxivPaper, ChatSession

logger = get_logger("Database")
qdrant_client: AsyncQdrantClient = None

async def init_database():
    """
    This function initializes the entire database connection.
    It is called only once during the lifespan of main.py.
    """
    logger.info("Establishing a database connection...")
    
    mongo_uri = os.getenv("MONGO_URI")
    qdrant_url = os.getenv("QDRANT_URL")
    
    if not mongo_uri or not qdrant_url:
        logger.error("Missing environment variables MONGO_URI or QDRANT_URL!")
        raise ValueError("Database configuration missing.")

    try:
        mongo_client = AsyncIOMotorClient(mongo_uri)
        db = mongo_client.get_default_database("arxiv_db")
        
        await init_beanie(database=db, document_models=[ArxivPaper, ChatSession])
        logger.info("✅ MongoDB & Beanie Connected!")
    except Exception as e:
        logger.error(f"❌ MongoDB connection error: {e}")
        raise e

    global qdrant_client
    try:
        qdrant_client = AsyncQdrantClient(url=qdrant_url)
        
        await qdrant_client.get_collections()
        logger.info("✅ Qdrant Connected!")
        
        await _ensure_qdrant_collection("arxiv_vectors")
        
    except Exception as e:
        logger.error(f"❌ Qdrant connection error: {e}")
        raise e

async def _ensure_qdrant_collection(collection_name: str):
    """
    Check if the collection already exists in Qdrant; if not, create a new one.
    """
    try:
        collections = await qdrant_client.get_collections()
        exists = any(c.name == collection_name for c in collections.collections)
        
        if not exists:
            logger.info(f"Creating a Qdrant collection: {collection_name}...")
            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=os.getenv("VECTOR_SIZE"),
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✅ Collection created {collection_name}")
        else:
            logger.debug(f"Collection {collection_name} already exists.")
            
    except Exception as e:
        logger.error(f"Error when checking/creating Qdrant collection: {e}")

def get_qdrant_client() -> AsyncQdrantClient:
    """Dependency to get the Qdrant client in other modules"""
    if qdrant_client is None:
        raise RuntimeError("The database has not been initialized yet! Please call init_database() first.")
    return qdrant_client