from pydantic import BaseModel
from typing import Optional, List


class LessonCreate(BaseModel):
    title: str
    description: str
    cause: Optional[str] = ""
    solution: Optional[str] = ""
    project_name: Optional[str] = ""
    project_type: Optional[str] = "Otro"
    created_by: Optional[str] = ""


class LessonResponse(BaseModel):
    id: int
    title: str
    description: str
    cause: str
    solution: str
    project_name: str
    project_type: str
    created_at: str
    created_by: str
    category: str
    severity: str
    phase: str
    tags: List[str]
    ai_processed: bool


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 6
    category: Optional[str] = None
    severity: Optional[str] = None


class SearchResult(BaseModel):
    lesson: LessonResponse
    score: float


class ReportRequest(BaseModel):
    query: str
    project_type: Optional[str] = None
    top_k: Optional[int] = 10
