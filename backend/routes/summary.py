# career_pathfinder/routes/summary.py

from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
# MODIFIED: Ensure SessionDetailsResponse is imported
from models import SessionFullDataResponse, SessionDetailsResponse, SessionDocument, CareerTrackDocument, RoadmapDocument, FullCareerTrack, RoadmapWeek, RoadmapTask
from bson import ObjectId
from typing import List

router = APIRouter()

# Existing endpoint for full session summary
@router.get("/session-summary/{session_id}", response_model=SessionFullDataResponse)
async def get_session_summary(session_id: str):
    """
    Retrieves a full summary of a user's session, including
    session details, recommended career tracks, and associated roadmaps.
    """
    db = get_database()

    # 1. Fetch Session Document
    session_doc_data = await db.Session.find_one({"_id": ObjectId(session_id)})
    if not session_doc_data:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session_details = SessionDocument(**session_doc_data)

    # 2. Fetch all Career Tracks for this session
    career_tracks_cursor = db.CareerTrack.find({"sessionId": session_id})
    career_tracks_data = await career_tracks_cursor.to_list(length=None)

    full_career_tracks: List[FullCareerTrack] = []

    # 3. For each Career Track, fetch its Roadmap
    for track_data in career_tracks_data:
        career_track_doc = CareerTrackDocument(**track_data)
        
        roadmap_for_track: Optional[List[RoadmapWeek]] = None
        
        roadmap_doc_data = await db.Roadmap.find_one({"trackId": str(career_track_doc.id)})
        
        if roadmap_doc_data:
            roadmap_doc = RoadmapDocument(**roadmap_doc_data)
            
            formatted_weeks: List[RoadmapWeek] = []
            for week_data in roadmap_doc.weeks:
                tasks_in_week = []
                for task_item in week_data.tasks:
                    tasks_in_week.append(RoadmapTask(
                        task=task_item.get('task') if isinstance(task_item, dict) else task_item.task,
                        isCompleted=task_item.get('isCompleted', False) if isinstance(task_item, dict) else task_item.isCompleted,
                        resourceLink=task_item.get('resourceLink') if isinstance(task_item, dict) else task_item.resourceLink
                    ))
                formatted_weeks.append(RoadmapWeek(week=week_data.week, tasks=tasks_in_week))
            roadmap_for_track = formatted_weeks
        
        full_career_tracks.append(FullCareerTrack(
            trackId=str(career_track_doc.id),
            title=career_track_doc.title,
            avgSalary=career_track_doc.avgSalary,
            skills=career_track_doc.skills,
            tools=career_track_doc.tools,
            growth=career_track_doc.growth,
            roadmap=roadmap_for_track
        ))

    return SessionFullDataResponse(
        sessionId=str(session_details.id),
        domain=session_details.domain,
        level=session_details.level,
        createdAt=session_details.createdAt,
        careerTracks=full_career_tracks
    )

# Existing endpoint for getting just particular session details by ID
@router.get("/session/{session_id}", response_model=SessionDetailsResponse)
async def get_session_details(session_id: str):
    """
    Retrieves basic details for a specific session by ID.
    """
    db = get_database()

    session_doc_data = await db.Session.find_one({"_id": ObjectId(session_id)})
    if not session_doc_data:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    session_details = SessionDocument(**session_doc_data)

    return SessionDetailsResponse(
        sessionId=str(session_details.id),
        domain=session_details.domain,
        level=session_details.level,
        createdAt=session_details.createdAt
    )

# NEW: Endpoint to get a list of all sessions
@router.get("/sessions", response_model=List[SessionDetailsResponse])
async def get_all_sessions():
    """
    Retrieves a list of basic details for all available sessions.
    """
    db = get_database()

    # Fetch all documents from the Session collection
    sessions_cursor = db.Session.find({})
    all_sessions_data = await sessions_cursor.to_list(length=None) # Get all results

    response_sessions = []
    for session_doc_data in all_sessions_data:
        session_details = SessionDocument(**session_doc_data)
        response_sessions.append(SessionDetailsResponse(
            sessionId=str(session_details.id),
            domain=session_details.domain,
            level=session_details.level,
            createdAt=session_details.createdAt
        ))
    
    return response_sessions