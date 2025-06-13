# app/models.py
from pydantic import BaseModel, HttpUrl
from typing import List

class QuestionRequest(BaseModel):
    """Input model for RAG query."""
    question: str

class Link(BaseModel):
    """Represents a single source link in the response."""
    url: HttpUrl
    text: str

class AnswerResponse(BaseModel):
    """Final structured JSON output from the assistant."""
    answer: str
    links: List[Link] = []
