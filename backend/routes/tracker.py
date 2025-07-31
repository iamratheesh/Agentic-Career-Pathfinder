
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
from models import RoadmapWeek, TaskUpdate, RoadmapDocument, RoadmapTask
from typing import List
from bson import ObjectId

router = APIRouter()

@router.get("/tracker/{session_id}", response_model=List[RoadmapWeek])
async def get_progress_tracker(session_id: str):
    """
    Retrieves the user's progress checklist for their active roadmap.
    """
    db = get_database()

    roadmap_doc = await db.Roadmap.find_one({"sessionId": session_id})
    if not roadmap_doc:
        raise HTTPException(status_code=404, detail="No roadmap found for this session.")

    formatted_weeks = []
    for week_data in roadmap_doc["weeks"]:
        tasks = []
        for task_item in week_data["tasks"]:
            tasks.append(RoadmapTask(
                task=task_item.get('task'),
                isCompleted=task_item.get('isCompleted', False),
                resourceLink=task_item.get('resourceLink') 
            ))
        formatted_weeks.append(RoadmapWeek(week=week_data["week"], tasks=tasks))

    return formatted_weeks

@router.patch("/tracker/{session_id}", response_model=RoadmapWeek) 
async def update_progress_tracker(session_id: str, task_update: TaskUpdate):
    """
    Updates the completion status and optionally the resource link of a specific task in the roadmap.
    """
    db = get_database()

    roadmap_doc = await db.Roadmap.find_one({"sessionId": session_id})
    if not roadmap_doc:
        raise HTTPException(status_code=404, detail="No roadmap found for this session.")

    found_week = None
    update_needed = False

    for week_idx, week_data in enumerate(roadmap_doc["weeks"]):
        if week_data["week"] == task_update.week:
            for task_idx, task_item in enumerate(week_data["tasks"]):
                if task_item["task"] == task_update.task:
                    if task_item.get("isCompleted") != task_update.status:
                        roadmap_doc["weeks"][week_idx]["tasks"][task_idx]["isCompleted"] = task_update.status
                        update_needed = True
                    
                    if task_update.resourceLink is not None and task_item.get("resourceLink") != task_update.resourceLink:
                        roadmap_doc["weeks"][week_idx]["tasks"][task_idx]["resourceLink"] = task_update.resourceLink
                        update_needed = True
                    elif task_update.resourceLink is None and task_item.get("resourceLink") is not None:
                         roadmap_doc["weeks"][week_idx]["tasks"][task_idx]["resourceLink"] = None
                         update_needed = True


                    found_week = roadmap_doc["weeks"][week_idx]
                    break 
            if found_week:
                break

    if not found_week:
        raise HTTPException(status_code=404, detail="Task or week not found in the roadmap.")

    if update_needed:
        await db.Roadmap.update_one(
            {"_id": roadmap_doc["_id"]},
            {"$set": {"weeks": roadmap_doc["weeks"]}}
        )
        return RoadmapWeek(week=found_week['week'], tasks=[RoadmapTask(**t) for t in found_week['tasks']])
    else:
        return RoadmapWeek(week=found_week['week'], tasks=[RoadmapTask(**t) for t in found_week['tasks']])