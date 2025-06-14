# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import app as fastapi_app
import uvicorn
import os

app = fastapi_app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only run locally
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # use Railway's PORT env
    uvicorn.run("api.index:app", host="0.0.0.0", port=port, reload=True)
