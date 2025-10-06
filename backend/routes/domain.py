
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from database import get_database
from models import DomainInput, InitDomainResponse, SessionDocument, QuizDocument, Question
from agents.strategy_questions import StrategyQuestionsAgent
from config import settings 
from bson import ObjectId

router = APIRouter()

@router.post("/init-domain", response_model=InitDomainResponse)
async def init_domain(domain_input: DomainInput):
    """
    Allows a user to input their domain of interest and initiates the quiz.
    """
    db = get_database()

    session_doc = SessionDocument(domain=domain_input.domain)
    inserted_session = await db.Session.insert_one(session_doc.model_dump(by_alias=True, exclude_none=True))
    session_id = str(inserted_session.inserted_id)

    questions_agent = StrategyQuestionsAgent(api_key=settings.GROQ_API_KEY ,resume_file="data/resume.txt")
    questions_list = await questions_agent.generate_questions(domain_input.domain)

    quiz_doc = QuizDocument(sessionId=session_id, questions=questions_list)
    inserted_quiz = await db.Quiz.insert_one(quiz_doc.model_dump(by_alias=True, exclude_none=True))
    quiz_id = str(inserted_quiz.inserted_id)

    response_questions = [Question(id=q['id'], question=q['question']) for q in questions_list]

    return InitDomainResponse(sessionId=session_id, quizId=quiz_id, questions=response_questions)