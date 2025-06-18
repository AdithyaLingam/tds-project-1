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
from playwright.sync_api import sync_playwright
from langchain_chroma import Chroma
from langchain.vectorstores.base import VectorStore
from openai import OpenAI
import requests 
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
BASE_URL = "https://tds.s-anand.net/#/2025-01/"
SAVE_DIR = Path("data/tds_pages_md")
DISCOURSE_JSON_DIR = "data/discourse_json"
VECTOR_STORE_DIR = "data/chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
# ---------------------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}

# ---------- SCRAPE COURSE PAGES ----------
def scrape_tds_pages():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        full_url = "https://tds.s-anand.net/#/2025-01/"
        print(f"Loading TOC from: {full_url}")
        page.goto(full_url, wait_until="networkidle")

        # Trigger rendering by waiting for sidebar links
        for i in range(60):
            links_count = page.evaluate("() => document.querySelectorAll('aside.sidebar a[href^=\"#/\"]').length")
            if links_count > 0:
                break
            print(f"Waiting for sidebar links... {i+1}s")
            time.sleep(1)
        else:
            raise TimeoutError("Sidebar links did not load in time.")

        links = page.evaluate("() => Array.from(document.querySelectorAll('aside.sidebar a[href^=\"#/\"]')).map(a => a.getAttribute('href'))")

        seen = set()
        for href in tqdm(links, desc="Scraping course pages"):
            if not href or href in seen:
                continue
            seen.add(href)

            # Navigate using JavaScript-based routing
            hash_url = "https://tds.s-anand.net/" + href
            try:
                page.goto(hash_url, wait_until="networkidle")
                page.wait_for_selector("article.markdown-section", timeout=10000)
                content = page.locator("article.markdown-section").inner_text()
                filename = href.strip("#/").replace("/", "_") + ".md"
                (SAVE_DIR / filename).write_text(content, encoding="utf-8")
            except Exception as e:
                print(f"Skipped {href}: {e}")

        browser.close()
    print(f"Scraped {len(seen)} pages into {SAVE_DIR}")


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
                    slug = data.get("slug", "-")
                    posts = data.get("post_stream", {}).get("posts", [])
                    for post in posts:
                        text = post.get("cooked") or post.get("raw") or ""
                        if text.strip():
                            metadata = {
                                "id": post.get("id"),
                                "topic_id": post.get("topic_id"),
                                "post_number": post.get("post_number"),
                                "created_at": post.get("created_at"),
                                "username": post.get("username"),
                                "source": f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{post.get('topic_id')}/{post.get('post_number')}"
                            }
                            documents.append(Document(page_content=text, metadata=metadata))
                        else:
                            skipped += 1
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    print(f"Loaded {len(documents)} documents. Skipped {skipped} empty posts.")
    return documents

def load_markdown_documents(md_dir: str) -> List[Document]:
    docs = []
    for md_file in md_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8").strip()
        if content:
            docs.append(Document(
                page_content=content,
                metadata={"source": BASE_URL + md_file.name.replace(".md", ".html")}
            ))
    print(f"Loaded {len(docs)} markdown documents.")
    return docs

def embed_with_retry(client: OpenAI, texts: list[str], retries: int = 3, delay: int = 2) -> list[list[float]]:
    # Sanitize input to be a list of clean strings
    cleaned_texts = [ str(t).strip()[:2000] for t in texts if isinstance(t, str) and t.strip() ]

    if not cleaned_texts:
        raise ValueError("No valid strings to embed.")

    all_embeddings = []

    # Chunk into batches
    batch_size = 100
    for i in tqdm(range(0, len(cleaned_texts), batch_size), desc="Embedding Progress", dynamic_ncols=True):
        batch = cleaned_texts[i:i+batch_size]

        for attempt in range(retries):
            try:
                print(f"[DEBUG] Embedding batch {i // batch_size + 1} with {len(batch)} texts...")
                response = client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=batch
                )
                all_embeddings.extend([d.embedding for d in response.data])
                break
            except Exception as e:
                print(f"Embedding failed on attempt {attempt+1}/{retries} for batch {i//batch_size + 1}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise

    return all_embeddings

# LangChain wrapper for OpenAI embeddings
class OpenAIEmbeddingsViaProxy(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return embed_with_retry(openai_client, texts)

    def embed_query(self, text: str) -> list[float]:
        return embed_with_retry(openai_client, [text])[0]

def main():
    scrape_tds_pages()

    discourse_docs = load_documents(DISCOURSE_JSON_DIR)
    markdown_docs = load_markdown_documents(SAVE_DIR)
    all_docs = discourse_docs + markdown_docs

    if not all_docs:
        print("No documents found.")
        return

    print(f"Splitting {len(all_docs)} documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(all_docs)

    if not chunks:
        print("No content to embed.")
        return

    print(f"Total chunks: {len(chunks)}")
    embedder = OpenAIEmbeddingsViaProxy()

    print("Building Chroma vector store...")
    vectordb = Chroma.from_documents(documents=chunks, embedding=embedder, persist_directory=str(VECTOR_STORE_DIR))
    print("Vector store built and saved.")

if __name__ == "__main__":
    main()