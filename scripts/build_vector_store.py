# scripts/build_vector_store.py
import os
import json
import time
from tqdm import tqdm 
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from langchain_community.vectorstores import Chroma
from langchain.vectorstores.base import VectorStore
from openai import OpenAI
from typing import List
from langchain.schema import Document
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Use AI Proxy endpoint
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)

# --- Hardcoded Configuration (except API key via os.getenv) ---
DISCOURSE_JSON_DIR = "data/discourse_json"
VECTOR_STORE_DIR = "data/chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
# ---------------------------------------------------------------

def load_documents(input_dir: str) -> List[Document]:
    documents = []
    skipped = 0

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(input_dir, filename)
            print(f"Reading: {filepath}")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Fix: properly access posts in 'post_stream'
                    posts = data.get("post_stream", {}).get("posts", [])
                    for post in posts:
                        text = post.get("cooked") or post.get("raw") or ""
                        if text.strip():
                            metadata = {
                                "id": post.get("id"),
                                "topic_id": post.get("topic_id"),
                                "post_number":post.get("post_number"),
                                "created_at": post.get("created_at"),
                                "username": post.get("username"),
                                "source": f"https://discourse.onlinedegree.iitm.ac.in/t/-/{post.get('topic_id')}/{post.get('post_number')}"
                            }
                            documents.append(Document(page_content=text, metadata=metadata))
                        else:
                            skipped += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"Loaded {len(documents)} documents. Skipped {skipped} empty posts.")
    return documents

def load_markdown_documents(md_dir: str) -> List[Document]:
    md_docs = []
    for path in Path(md_dir).rglob("*.md"):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                md_docs.append(Document(page_content=content, metadata={"source": str(path)}))
    print(f"Loaded {len(md_docs)} markdown documents.")
    return md_docs

def embed_with_retry(client: OpenAI, texts: list[str], retries: int = 3, delay: int = 2) -> list[list[float]]:
    # Sanitize input to be a list of clean strings
    cleaned_texts = [
        str(t).strip()[:2000] for t in texts
        if isinstance(t, str) and t.strip()
    ]

    if not cleaned_texts:
        raise ValueError("No valid strings to embed.")

    print(f"[DEBUG] Sending {len(cleaned_texts)} texts for embedding")

    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=cleaned_texts
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            print(f"Embedding failed on attempt {attempt+1}/{retries}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

# LangChain wrapper for OpenAI embeddings
class OpenAIEmbeddingsViaProxy(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_with_retry(openai_client, texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_with_retry(openai_client, [text])[0]

def main():
    print("Loading documents...")
    discourse_docs = load_documents(DISCOURSE_JSON_DIR)
    print("Loading Markdown pages...")
    markdown_docs = load_markdown_documents("data/tds_pages_md")

    docs = discourse_docs + markdown_docs

    if not docs:
        print("No documents found. Exiting.")
        return
    print(f"Loaded {len(docs)} documents.")

    print("Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = splitter.split_documents(docs)
    if not split_docs:
        print("No content to embed. Exiting.")
        return

    print(f"Total chunks: {len(split_docs)}")
    embedder = OpenAIEmbeddingsViaProxy()

    print("Building Chroma vector store in batches...")
    batch_size = 100
    vectordb = None

    for i in tqdm(range(0, len(split_docs), batch_size)):
        batch = split_docs[i:i + batch_size]
        print(f"[DEBUG] Embedding batch {i//batch_size + 1} with {len(batch)} documents...")

        if vectordb is None:
            vectordb = Chroma.from_documents(
                documents=batch,
                embedding=embedder,
                persist_directory=VECTOR_STORE_DIR
            )
        else:
            vectordb.add_documents(batch)

    vectordb.persist()
    print(f"Vector store built and saved to: {VECTOR_STORE_DIR}")

if __name__ == "__main__":
    main()

