#app/rag_pipeline.py
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Extra

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    DATA_DIR: Path = BASE_DIR / "data"
    DISCOURSE_JSON_DIR: Path = DATA_DIR / "discourse_json"
    VECTOR_STORE_DIR: Path = DATA_DIR / "chroma_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "llama3"  # or "mistral", "phi", etc.
    OLLAMA_HOST: str = "http://localhost:11434"

    class Config:
        env_file = ".env"
        extra = Extra.allow

settings = Settings()
