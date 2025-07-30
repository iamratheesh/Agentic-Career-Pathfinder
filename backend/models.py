# career_pathfinder/models.py

from pydantic import BaseModel, Field, BeforeValidator, HttpUrl
from typing import List, Optional, Annotated
from datetime import datetime
from bson import ObjectId

# Custom type for handling ObjectId in Pydantic V2
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- Request Models ---

class DomainInput(BaseModel):
    domain: str = Field(..., description="User's chosen domain of interest, e.g., 'Frontend Developer'")

class QuizAnswer(BaseModel):
    question: str
    answer: str

class QuizSubmission(BaseModel):
    sessionId: str
    quizId: str
    answers: List[QuizAnswer]

class TaskUpdate(BaseModel):
    week: int
    task: str
    status: bool
    resourceLink: Optional[str] = None # For manual updates to resource link

# --- Response Models ---

class Question(BaseModel):
    id: int
    question: str

class InitDomainResponse(BaseModel):
    sessionId: str
    quizId: str
    questions: List[Question]

class LevelPredictionResponse(BaseModel):
    level: str # e.g., "Beginner", "Intermediate", "Advanced"
    nextStep: str # e.g., "career-track-recommendation"

class CareerTrack(BaseModel):
    title: str # e.g., "React Developer"
    avgSalary: str # e.g., "8-12 LPA"
    skills: List[str] # e.g., ["React", "Redux"]
    tools: List[str] # e.g., ["Vite", "Next.js"]
    growth: str # e.g., "Can become Frontend Architect"

class RoadmapTask(BaseModel):
    task: str
    isCompleted: bool = False
    resourceLink: Optional[str] = None # <--- THIS MUST BE 'str'

class RoadmapWeek(BaseModel):
    week: int
    tasks: List[RoadmapTask]

# --- MongoDB Document Models (for internal use, not directly for API response unless needed) ---

class SessionDocument(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None) # For MongoDB _id, optional on creation
    domain: str
    level: Optional[str] = None # Will be populated later
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True # Pydantic V2 equivalent of allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: str} # Ensure ObjectId is serialized to str

class QuizDocument(BaseModel):
    sessionId: str
    questions: List[dict] # Storing questions as dicts from the agent
    answers: List[QuizAnswer] = [] # Storing Q&A pairs as QuizAnswer models

    class Config:
        arbitrary_types_allowed = True

class CareerTrackDocument(BaseModel):
    sessionId: str
    title: str
    avgSalary: str
    skills: List[str]
    tools: List[str]
    growth: str

    class Config:
        arbitrary_types_allowed = True

class RoadmapDocument(BaseModel):
    sessionId: str
    trackId: str
    weeks: List[RoadmapWeek]

    class Config:
        arbitrary_types_allowed = True