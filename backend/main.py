# career_pathfinder/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Import database connection
from database import connect_to_mongodb, close_mongodb_connection

# Import API routes
from routes import domain, quiz, career, roadmap, tracker

load_dotenv() # Load environment variables from .env file

app = FastAPI(
    title="Agentic Career Pathfinder API",
    description="AI-powered personalized career guidance system for students.",
    version="1.0.0"
)

# Event handlers for application startup and shutdown
@app.on_event("startup")
async def startup_event():
    """Connects to MongoDB when the application starts."""
    await connect_to_mongodb()
    print("Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_event():
    """Closes the MongoDB connection when the application shuts down."""
    await close_mongodb_connection()
    print("Disconnected from MongoDB")

# Include routers for different API endpoints
app.include_router(domain.router, tags=["Domain Selection"])
app.include_router(quiz.router, tags=["Quiz & Skill Assessment"])
app.include_router(career.router, tags=["Career Tracks"])
app.include_router(roadmap.router, tags=["Roadmap Generation"])
app.include_router(tracker.router, tags=["Progress Tracker"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic Career Pathfinder API"}

# To run this file:
# uvicorn main:app --reload