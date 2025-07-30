# career_pathfinder/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware # NEW: Import CORSMiddleware


# Import database connection
from database import connect_to_mongodb, close_mongodb_connection

# Import API routes
from routes import domain, quiz, career, roadmap, tracker, summary

load_dotenv() # Load environment variables from .env file



app = FastAPI(
    title="Agentic Career Pathfinder API",
    description="AI-powered personalized career guidance system for students.",
    version="1.0.0"
)

# CORRECT: CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins. For production, replace "*" with specific frontend origins, e.g., ["http://localhost:5173", "https://your-frontend.com"]
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"], 
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
app.include_router(summary.router, tags=["Session Summary"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Agentic Career Pathfinder API"}

# To run this file:
# uvicorn main:app --reload