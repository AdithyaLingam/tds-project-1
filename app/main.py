# app/main.py

import json
from fastapi import FastAPI, HTTPException, Request
from app.models import QARequest, QAResponse
from app.rag_pipeline import query_and_generate
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="TDS Virtual TA API",
    description="API for answering questions about the Tools in Data Science course."
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/", include_in_schema=False)
def root():
    return {"message": "TDS Virtual TA API is running."}

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.post("/api/", response_model=QAResponse)
async def get_answer(request: QARequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        response_text = query_and_generate(request.question, request.image)
        return QAResponse(**response_text)
    except Exception as e:
        return QAResponse(answer=f"Backend is working! Error: {e}", links=[])

@app.get("/ask", response_model=QAResponse)
async def ask(query: str):
    try:
        response_text = query_and_generate(query)
        return QAResponse(**response_text)
    except Exception as e:
        return QAResponse(answer=f"Backend is working! Error: {e}", links=[])
