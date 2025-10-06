
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
from models import CareerTrack, SessionDocument, CareerTrackDocument, FullCareerTrack, EnrollTrackUpdate
from agents.track_recommender import CareerTrackRecommenderAgent
from config import settings
from typing import List
from bson import ObjectId

router = APIRouter()

@router.get("/career-tracks/{session_id}", response_model=List[FullCareerTrack])
async def get_career_tracks(session_id: str):
    """
    Generates and returns career track recommendations based on user's domain and skill level.
    """
    db = get_database()

    session_doc = await db.Session.find_one({"_id": ObjectId(session_id)})
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session_doc.get("level"):
        raise HTTPException(status_code=400, detail="User level not yet determined. Complete the quiz first.")

    domain = session_doc["domain"]
    level = session_doc["level"]

    recommender_agent = CareerTrackRecommenderAgent(
        api_key=settings.GROQ_API_KEY,
        tavily_api_key=settings.TAVILY_API_KEY
    )
    
    try:
        llm_recommended_tracks = await recommender_agent.recommend_tracks(domain, level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate career tracks due to agent error: {e}")

    if not llm_recommended_tracks:
        raise HTTPException(status_code=500, detail="Failed to generate any career tracks. Agent returned empty list.")

    for track_data in llm_recommended_tracks:
        track_doc = CareerTrackDocument(sessionId=session_id, **track_data)
        
        await db.CareerTrack.update_one(
            {"sessionId": session_id, "title": track_data["title"]},
            {"$set": track_doc.model_dump(by_alias=True, exclude_none=True)},
            upsert=True 
        )

    fetched_career_tracks_cursor = db.CareerTrack.find({"sessionId": session_id})
    fetched_career_tracks_data = await fetched_career_tracks_cursor.to_list(length=None)

    response_tracks = []
    for track_doc_data in fetched_career_tracks_data:
        response_tracks.append(FullCareerTrack(**track_doc_data))

    return response_tracks



@router.patch("/career-tracks/{track_id}/enroll", response_model=FullCareerTrack)
async def update_career_track_enrollment(track_id: str, enroll_update: EnrollTrackUpdate):
    """
    Updates the enrollment status of a specific career track.
    """
    db = get_database()

    existing_track = await db.CareerTrack.find_one({"_id": ObjectId(track_id)})
    if not existing_track:
        raise HTTPException(status_code=404, detail="Career track not found.")

    result = await db.CareerTrack.update_one(
        {"_id": ObjectId(track_id)},
        {"$set": {"isEnrolled": enroll_update.isEnrolled}}
    )

    if result.modified_count == 0:
        updated_track_data = await db.CareerTrack.find_one({"_id": ObjectId(track_id)})
        if not updated_track_data: 
             raise HTTPException(status_code=404, detail="Career track not found after update attempt.")
        return FullCareerTrack(**updated_track_data)
    
    updated_track_data = await db.CareerTrack.find_one({"_id": ObjectId(track_id)})
    
    return FullCareerTrack(**updated_track_data)