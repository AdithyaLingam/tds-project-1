# app/main.py
import json
from fastapi import FastAPI, HTTPException
from .models import QuestionRequest, AnswerResponse
from .rag_pipeline import query_and_generate

app = FastAPI(
    title="TDS Virtual TA API",
    description="API for answering questions about the Tools in Data Science course.",
    version="0.1.0"
)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "TDS Virtual TA API is running."}

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

@app.post("/api/", response_model=AnswerResponse)
async def get_answer(request: QuestionRequest):
    """
    Accepts a student's question and returns a generated answer with sources.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:

        llm_response_json = query_and_generate(request.question)

        response_data = json.loads(llm_response_json)
        
        return AnswerResponse(**response_data)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the question.")

@app.get("/ask", response_model=AnswerResponse)
async def ask(query: str):
    """
    Allows quick testing via browser query param.
    """
    try:
        llm_response_json = query_and_generate(query)
        response_data = json.loads(llm_response_json)
        return AnswerResponse(**response_data)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the query.")
