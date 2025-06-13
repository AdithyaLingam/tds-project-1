import json
from fastapi import APIRouter, HTTPException, FastAPI
from .models import QuestionRequest, AnswerResponse
from .rag_pipeline import query_and_generate

app = FastAPI(
    title="TDS Virtual TA API",
    description="API for answering questions about the Tools in Data Science course."
)

@app.get("/")
def read_root():
    return {"message": "OK"}

# Define the router
router = APIRouter()

@router.get("/", include_in_schema=False)
def read_root():
    return {"message": "TDS Virtual TA API is running."}

@router.post("/api/", response_model=AnswerResponse)
async def get_answer(request: QuestionRequest):
    """
    Accepts a student's question and returns a generated answer with sources.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    print(f"Received question: {request.question}")
    
    try:
        # This function now handles querying and generation
        llm_response_json = query_and_generate(request.question)
        
        # The LLM is prompted to return a JSON string, so we parse it
        response_data = json.loads(llm_response_json)

        # Validate with our Pydantic model before returning
        return AnswerResponse(**response_data)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the question.")

@router.get("/ask", response_model=AnswerResponse)
async def ask(query: str):
    llm_response_json = query_and_generate(query)
    response_data = json.loads(llm_response_json)
    return AnswerResponse(**response_data)

@router.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

app.include_router(router)