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
    resourceLink: Optional[str] = None

# --- Response Models ---

class Question(BaseModel):
    id: int
    question: str

class InitDomainResponse(BaseModel):
    sessionId: str
    quizId: str
    questions: List[Question]

class LevelPredictionResponse(BaseModel):
    level: str
    nextStep: str

class CareerTrack(BaseModel): # Basic CareerTrack for LLM output and general use
    title: str
    avgSalary: str
    skills: List[str]
    tools: List[str]
    growth: str

class RoadmapTask(BaseModel):
    task: str
    isCompleted: bool = False
    resourceLink: Optional[str] = None

class RoadmapWeek(BaseModel):
    week: int
    tasks: List[RoadmapTask]

# Model to represent a career track with its optional roadmap (for response)
class FullCareerTrack(BaseModel):
    trackId: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    avgSalary: str
    skills: List[str]
    tools: List[str]
    growth: str
    roadmap: Optional[List[RoadmapWeek]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

# The main response model for the session summary (already correct for its purpose)
class SessionFullDataResponse(BaseModel):
    sessionId: str
    domain: str
    level: Optional[str] = None
    createdAt: datetime
    careerTracks: List[FullCareerTrack] = []

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: str
        }

# NEW: Response model for just basic session details
class SessionDetailsResponse(BaseModel):
    sessionId: str
    domain: str
    level: Optional[str] = None
    createdAt: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: str
        }


# --- MongoDB Document Models (for internal use, not directly for API response unless needed) ---

class SessionDocument(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    domain: str
    level: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: str}

class CareerTrackDocument(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    sessionId: str
    title: str
    avgSalary: str
    skills: List[str]
    tools: List[str]
    growth: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

class QuizDocument(BaseModel):
    sessionId: str
    questions: List[dict]
    answers: List[QuizAnswer] = []

    class Config:
        arbitrary_types_allowed = True

class RoadmapDocument(BaseModel):
    sessionId: str
    trackId: str
    weeks: List[RoadmapWeek]

    class Config:
        arbitrary_types_allowed = True