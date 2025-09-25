from .config import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import MONGO_DATABASE_HOST, MONGO_DATABASE_NAME
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Load environment variables from .env file

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# Dependency to get the DB session
async def get_db():
    async with SessionLocal() as session:
        yield session

mongo_client = AsyncIOMotorClient(MONGO_DATABASE_HOST)
mongo_db: AsyncIOMotorDatabase = mongo_client[MONGO_DATABASE_NAME]

# Export collections (optional)
master_medicine_collection = mongo_db["master_medicine"]
wishlist_collection = mongo_db["wishlist"]

# Dependency for MongoDB
async def get_mongo_db() -> AsyncIOMotorDatabase:
    return mongo_db