# career_pathfinder/routes/roadmap.py

from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
# Removed HttpUrl from this import line as it's not needed for direct type hinting in routes now
from models import RoadmapWeek, RoadmapDocument, SessionDocument, CareerTrackDocument, RoadmapTask
from agents.roadmap_generator import RoadmapGeneratorAgent
from config import settings
from typing import List
from bson import ObjectId
import json # Import json for pretty printing debug output

router = APIRouter()

@router.get("/roadmap/{track_id}", response_model=List[RoadmapWeek])
async def get_roadmap(track_id: str):
    """
    Generates and returns a weekly roadmap for a specific career track.
    """
    db = get_database()

    career_track_doc = await db.CareerTrack.find_one({"_id": ObjectId(track_id)})
    if not career_track_doc:
        raise HTTPException(status_code=404, detail="Career track not found.")

    session_id = str(career_track_doc["sessionId"])
    session_doc = await db.Session.find_one({"_id": ObjectId(session_id)})
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found for this track.")
    if not session_doc.get("level"):
        raise HTTPException(status_code=400, detail="User level not yet determined.")

    domain = session_doc["domain"]
    level = session_doc["level"]

    # Check if a roadmap already exists for this trackId
    existing_roadmap = await db.Roadmap.find_one({"trackId": track_id})
    if existing_roadmap:
        formatted_existing_weeks = []
        for week_data in existing_roadmap["weeks"]:
            tasks = []
            for task_item in week_data["tasks"]:
                # Ensure resourceLink is explicitly a string or None for RoadmapTask
                tasks.append(RoadmapTask(
                    task=task_item.get('task'),
                    isCompleted=task_item.get('isCompleted', False),
                    resourceLink=str(task_item['resourceLink']) if task_item.get('resourceLink') else None
                ))
            formatted_existing_weeks.append(RoadmapWeek(week=week_data["week"], tasks=tasks))
        return formatted_existing_weeks


    # Prompt Groq for roadmap generation
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

    # Convert tasks from agent output (dict) to RoadmapTask object
    formatted_weeks = []
    for week_data in generated_weeks_data:
        tasks_with_status = []
        for task_item in week_data['tasks']:
            # *** CRITICAL FIX HERE: Explicitly convert to string for resourceLink ***
            # This ensures that even if HttpUrl objects somehow exist in task_item.get('resourceLink'),
            # they are converted to strings before being passed to RoadmapTask.
            # If task_item.get('resourceLink') is already a string or None, it remains so.
            resource_link_value = task_item.get('resourceLink')
            if resource_link_value is not None:
                resource_link_value = str(resource_link_value) # Convert to string
            
            # DEBUGGING ADDITION: Print type of the value being used before creating RoadmapTask
            print(f"DEBUG: ResourceLink value before RoadmapTask creation for task '{task_item.get('task')}': {type(resource_link_value)}, Value: {resource_link_value}")

            tasks_with_status.append(RoadmapTask(
                task=task_item.get('task'),
                isCompleted=False,
                resourceLink=resource_link_value # Pass the string/None value
            ))
        formatted_weeks.append(RoadmapWeek(week=week_data['week'], tasks=tasks_with_status))

    # Store in Roadmap collection
    roadmap_doc = RoadmapDocument(sessionId=session_id, trackId=track_id, weeks=formatted_weeks)

    # *** DEBUGGING ADDITION: Print type from Pydantic model instance just before model_dump ***
    for week_debug in roadmap_doc.weeks:
        for task_debug in week_debug.tasks:
            print(f"DEBUG: Type of resourceLink IN RoadmapTask Pydantic model before model_dump for task '{task_debug.task}': {type(task_debug.resourceLink)}, Value: {task_debug.resourceLink}")


    # *** DEBUGGING ADDITION: Print the document before insertion ***
    debug_dict_to_insert = roadmap_doc.model_dump(by_alias=True, exclude_none=True)
    print("\nDEBUG: Final document structure for MongoDB insertion:")
    print(json.dumps(debug_dict_to_insert, indent=2)) # Pretty print the dictionary for easy inspection
    print("--- END DEBUG PRINT ---\n")

    await db.Roadmap.insert_one(debug_dict_to_insert)

    return formatted_weeks