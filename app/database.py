import os
import certifi
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "research_agent_db")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL is missing")

client = AsyncIOMotorClient(
    MONGODB_URL,
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=30000
)

db = client[DATABASE_NAME]

users_collection = db["users"]
research_logs_collection = db["research_logs"]