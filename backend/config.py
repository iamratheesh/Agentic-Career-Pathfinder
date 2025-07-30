# career_pathfinder/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Ensure this exactly matches how your MongoDB is configured
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/pathfinder")
    DB_NAME: str = os.getenv("DB_NAME", "pathfinder")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "YOUR_TAVILY_API_KEY")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY")

settings = Settings()