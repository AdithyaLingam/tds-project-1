# app/rag_pipeline.py
import os
import base64
import requests
import tempfile
from io import BytesIO
from typing import List, Tuple, Optional
from PIL import Image
import pytesseract
from app.config import settings
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain.vectorstores.base import VectorStoreRetriever

CHROMA_PATH = "data/chroma_db/"

embedding_model = OpenAIEmbeddings(
    model=settings.EMBEDDING_MODEL,
    openai_api_base="https://aiproxy.sanand.workers.dev/openai/v1",
    openai_api_key=settings.OPENAI_API_KEY
)

vector_store = Chroma(
    persist_directory=str(settings.VECTOR_STORE_DIR),
    embedding_function=embedding_model
)

retriever = vector_store.as_retriever()

def get_vectorstore():
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_model)

def build_docs_from_texts(texts: List[str]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    documents = splitter.create_documents(texts)
    return documents

def generate_embeddings(texts: List[str]):
    vectorstore = get_vectorstore()
    documents = build_docs_from_texts(texts)
    vectorstore.add_documents(documents)
    vectorstore._client.persist()

def ask_question(question: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful Teaching Assistant for the Tools in Data Science course."},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(
        "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    if response.status_code != 200:
        return f"Backend is working! Error: Error code: {response.status_code} - {response.text}"
    return response.json()["choices"][0]["message"]["content"]

# --- OCR for image input ---
def process_image(base64_image: str) -> str:
    try:
        if base64_image.startswith("data:image"):
            base64_image = base64_image.split(",")[1]
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        return f"[OCR Error: {str(e)}]"

# --- Query & generate answer ---
def query_and_generate(question: str, image_b64: Optional[str] = None) -> dict:
    extracted_text = process_image(image_b64) if image_b64 else ""
    full_prompt = f"{question}\n\n{extracted_text}".strip()

    results: List[Tuple[Document, float]] = vector_store.similarity_search_with_score(full_prompt, k=6)
    relevant_docs = [doc for doc, score in results if score is None or score >= 0.2 and "score" in doc.page_content.lower()]
    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    messages = [
        {"role": "system", "content": "You are a teaching assistant answering questions using the Tools in Data Science course material."},
        {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"}
    ]

    try:
        response = requests.post(
            "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": settings.LLM_MODEL,
                "messages": messages
            }
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"].strip()

        links = []
        for doc in relevant_docs:
            source = doc.metadata.get("source")
            if source:
                links.append({
                    "url": source,
                    "text": doc.metadata.get("title", "Related discussion")
                })

        return {
            "answer": answer,
            "links": links
        }

    except Exception as e:
        return {
            "answer": f"Backend is working! Error: {str(e)}",
            "links": []
        }