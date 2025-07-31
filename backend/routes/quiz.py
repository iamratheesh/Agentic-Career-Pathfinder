
import time
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
from models import QuizSubmission, LevelPredictionResponse, SessionDocument, QuizDocument
from agents.level_detector import LevelDetectorAgent
from config import settings
from bson import ObjectId

router = APIRouter()

@router.post("/submit-answer", response_model=LevelPredictionResponse)
async def submit_answers(submission_data: QuizSubmission):
    db = get_database()

    quiz_doc = await db.Quiz.find_one({"_id": ObjectId(submission_data.quizId), "sessionId": submission_data.sessionId})

    if not quiz_doc:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if len(submission_data.answers) != 10:
        raise HTTPException(status_code=400, detail="Exactly 10 answers must be submitted.")

    quiz_doc['answers'] = [answer.model_dump() for answer in submission_data.answers]

    await db.Quiz.update_one(
        {"_id": ObjectId(submission_data.quizId)},
        {"$set": {"answers": quiz_doc['answers']}}
    )

    level_detector_agent = LevelDetectorAgent(api_key=settings.GROQ_API_KEY)
    predicted_level = await level_detector_agent.detect_level(quiz_doc['answers'])

    await db.Session.update_one(
        {"_id": ObjectId(submission_data.sessionId)},
        {"$set": {"level": predicted_level}}
    )


    return LevelPredictionResponse(level=predicted_level, nextStep="career-track-recommendation")