#api/index.py
import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from app.main import app as fastapi_app

# Assign FastAPI app instance
app = fastapi_app

# Add CORS middleware AFTER app is defined
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render's injected PORT
    uvicorn.run("api.index:app", host="0.0.0.0", port=port)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "TDS Virtual TA API is running."}