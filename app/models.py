# app/models.py
from pydantic import BaseModel
from typing import List, Optional

class Link(BaseModel):
    url: str
    text: str

class QARequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 string

class QAResponse(BaseModel):
    answer: str
    links: List[Link] = []

