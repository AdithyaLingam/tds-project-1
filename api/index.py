# api/index.py
# This file is the entry point for Vercel's serverless functions.
# It imports the main FastAPI app instance.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import app as fastapi_app
import uvicorn
import os

app = fastapi_app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



