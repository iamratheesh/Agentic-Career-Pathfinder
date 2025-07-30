# career_pathfinder/routes/quiz.py

import time # Keep for potential timing prints
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
from models import QuizSubmission, LevelPredictionResponse, SessionDocument, QuizDocument
from agents.level_detector import LevelDetectorAgent
from config import settings # Import settings
from bson import ObjectId

router = APIRouter()

@router.post("/submit-answer", response_model=LevelPredictionResponse)
async def submit_answers(submission_data: QuizSubmission):
    # Optional: Keep timing prints for performance debugging if needed
    # start_total = time.perf_counter()
    db = get_database()

    # Find the quiz document
    # start_db_find = time.perf_counter()
    quiz_doc = await db.Quiz.find_one({"_id": ObjectId(submission_data.quizId), "sessionId": submission_data.sessionId})
    # end_db_find = time.perf_counter()
    # print(f"Time for db.Quiz.find_one: {end_db_find - start_db_find:.4f} seconds")

    if not quiz_doc:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if len(submission_data.answers) != 10:
        raise HTTPException(status_code=400, detail="Exactly 10 answers must be submitted.")

    quiz_doc['answers'] = [answer.model_dump() for answer in submission_data.answers]

    # start_db_update = time.perf_counter()
    await db.Quiz.update_one(
        {"_id": ObjectId(submission_data.quizId)},
        {"$set": {"answers": quiz_doc['answers']}}
    )
    # end_db_update = time.perf_counter()
    # print(f"Time for db.Quiz.update_one: {end_db_update - start_db_update:.4f} seconds")

    # Use the Groq API key
    level_detector_agent = LevelDetectorAgent(api_key=settings.GROQ_API_KEY)
    # start_llm_call = time.perf_counter()
    predicted_level = await level_detector_agent.detect_level(quiz_doc['answers'])
    # end_llm_call = time.perf_counter()
    # print(f"Time for LLM call (detect_level): {end_llm_call - start_llm_call:.4f} seconds")

    # Update the session with the predicted level
    # start_db_session_update = time.perf_counter()
    await db.Session.update_one(
        {"_id": ObjectId(submission_data.sessionId)},
        {"$set": {"level": predicted_level}}
    )
    # end_db_session_update = time.perf_counter()
    # print(f"Time for db.Session.update_one: {end_db_session_update - start_db_session_update:.4f} seconds")

    # end_total = time.perf_counter()
    # print(f"Total /submit-answers endpoint time: {end_total - start_total:.4f} seconds")

    return LevelPredictionResponse(level=predicted_level, nextStep="career-track-recommendation")