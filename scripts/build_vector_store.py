# scripts/build_vector_store.py

import os
import json
import time
from bs4 import BeautifulSoup
import chromadb
from openai import OpenAI

# --- Hardcoded Configuration (except API key via os.getenv) ---
DISCOURSE_JSON_DIR = "data/discourse_json"
VECTOR_STORE_DIR = "data/chroma_db"
EMBEDDING_MODEL = "text-embedding-3-small"
# ---------------------------------------------------------------

def load_all_documents():
    docs, ids, metas = [], [], []
    seen = set()
    for file in os.listdir(DISCOURSE_JSON_DIR):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(DISCOURSE_JSON_DIR, file), encoding="utf-8") as f:
            topic = json.load(f)

        slug = topic.get("slug", "")
        tid = topic.get("id", "")
        url = f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{tid}"
        title = topic.get("title", "")

        for post in topic.get("post_stream", {}).get("posts", []):
            pid = post["id"]
            content = post.get("cooked", "")
            if not content:
                continue
            text = BeautifulSoup(content, "html.parser").get_text().strip()
            if not text or f"post_{pid}" in seen:
                continue

            seen.add(f"post_{pid}")
            docs.append(text)
            ids.append(f"post_{pid}")
            metas.append({
                "source": url,
                "title": title,
                "post_number": post.get("post_number")
            })
    return docs, ids, metas

def embed_with_retry(client, texts, retries=3, delay=2):
    for attempt in range(retries):
        try:
            resp = client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
            return [r.embedding for r in resp.data]
        except Exception as e:
            print(f"Retry {attempt + 1}: {e}")
            time.sleep(delay)
    raise RuntimeError("Failed to embed after retries.")

def main():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise EnvironmentError("OPENAI_API_KEY not found in environment variables.")

    print("Loading documents...")
    docs, ids, metas = load_all_documents()
    print(f"Loaded {len(docs)} documents.")

    client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
    collection = client.get_or_create_collection(name="tds_virtual_ta")
    openai_client = os.getenv("OPENAI_API_KEY")

    for i in range(0, len(docs), 100):
        print(f"Embedding batch {i//100 + 1}...")
        batch_docs = docs[i:i+100]
        batch_ids = ids[i:i+100]
        batch_metas = metas[i:i+100]
        embeds = embed_with_retry(openai_client, batch_docs)
        collection.add(documents=batch_docs, metadatas=batch_metas, embeddings=embeds, ids=batch_ids)

    print(f"Completed. Total in collection: {collection.count()}")

if __name__ == "__main__":
    main()
