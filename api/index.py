# api/index.py
# This file is the entry point for Vercel's serverless functions.
# It imports the main FastAPI app instance.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import router as api_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main router
app.include_router(api_router)
