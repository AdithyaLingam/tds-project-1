# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.main import app as fastapi_app
import uvicorn
import os

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

