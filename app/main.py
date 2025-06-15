# app/main.py

import base64
from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.rag_pipeline import query_and_generate

app = FastAPI(
    title="TDS Virtual TA API",
    description="API for answering questions about the Tools in Data Science course."
)

# Allow all CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def form_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    question: str = Form(...),
    image: UploadFile = File(None)
):
    image_preview = None
    image_base64 = None

    if image:
        try:
            image_bytes = await image.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            image_preview = f"data:{image.content_type};base64,{image_base64}"
        except Exception as e:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "question": question,
                "answer": f"Error reading image: {e}"
            })

    try:
        result = query_and_generate(question, image_base64)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "question": question,
            "image_preview": image_preview,
            "answer": result["answer"],
            "links": result.get("links", [])
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "question": question,
            "answer": f"Backend is working! Error: {str(e)}"
        })
