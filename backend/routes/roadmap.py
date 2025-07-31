
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
from models import RoadmapWeek, RoadmapDocument, SessionDocument, CareerTrackDocument, RoadmapTask, FullCareerTrack, SingleTrackWithRoadmapResponse
from agents.roadmap_generator import RoadmapGeneratorAgent
from config import settings
from typing import List
from bson import ObjectId
import json
import traceback

router = APIRouter()

@router.get("/roadmap/{track_id}", response_model=SingleTrackWithRoadmapResponse)
async def get_roadmap(track_id: str):
    """
    Generates and returns a specific career track's details along with its weekly roadmap.
    """
    db = get_database()

    career_track_doc_data = await db.CareerTrack.find_one({"_id": ObjectId(track_id)})
    if not career_track_doc_data:
        raise HTTPException(status_code=404, detail="Career track not found.")
    
    career_track_db_model = CareerTrackDocument(**career_track_doc_data)
    
    career_track_response_model = FullCareerTrack(**career_track_doc_data)

    session_id = str(career_track_db_model.sessionId) 
    session_doc = await db.Session.find_one({"_id": ObjectId(session_id)})
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found for this track.")
    if not session_doc.get("level"):
        raise HTTPException(status_code=400, detail="User level not yet determined. Complete the quiz first.")

    domain = session_doc["domain"]
    level = session_doc["level"]

    existing_roadmap_doc_data = await db.Roadmap.find_one({"trackId": track_id})
    
    roadmap_weeks: List[RoadmapWeek] = []

    if existing_roadmap_doc_data:
        roadmap_doc = RoadmapDocument(**existing_roadmap_doc_data)
        for week_data in roadmap_doc.weeks:
            tasks = []
            for task_item in week_data.tasks:
                tasks.append(RoadmapTask(
                    task=task_item.get('task') if isinstance(task_item, dict) else task_item.task,
                    isCompleted=task_item.get('isCompleted', False) if isinstance(task_item, dict) else task_item.isCompleted,
                    resourceLink=task_item.get('resourceLink') if isinstance(task_item, dict) else task_item.resourceLink
                ))
            roadmap_weeks.append(RoadmapWeek(week=week_data.week, tasks=tasks))
    else:
        roadmap_agent = RoadmapGeneratorAgent(
            api_key=settings.GROQ_API_KEY,
            tavily_api_key=settings.TAVILY_API_KEY
        )
        
        try:
            generated_weeks_data = await roadmap_agent.generate_roadmap(domain, level)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate roadmap due to agent error: {e}")

        if not generated_weeks_data:
            raise HTTPException(status_code=500, detail="Failed to generate roadmap. Agent returned empty list or invalid format.")

        for week_data in generated_weeks_data:
            tasks_with_status = []
            for task_item in week_data['tasks']:
                resource_link_value = task_item.get('resourceLink')
                if resource_link_value is not None:
                    resource_link_value = str(resource_link_value)
                
                tasks_with_status.append(RoadmapTask(
                    task=task_item.get('task'),
                    isCompleted=False,
                    resourceLink=resource_link_value
                ))
            roadmap_weeks.append(RoadmapWeek(week=week_data['week'], tasks=tasks_with_status))

        roadmap_doc = RoadmapDocument(sessionId=session_id, trackId=track_id, weeks=roadmap_weeks)
        await db.Roadmap.insert_one(roadmap_doc.model_dump(by_alias=True, exclude_none=True))

    return SingleTrackWithRoadmapResponse(
        track=career_track_response_model,
        roadmap=roadmap_weeks
    )