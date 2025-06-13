from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Extra


# Define project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Centralized settings class
class Settings(BaseSettings):
    # Required credentials
    OPENAI_API_KEY: str | None = None  # Made optional if Ollama is used instead

    # Directory paths
    DATA_DIR: Path = BASE_DIR / "data"
    DISCOURSE_JSON_DIR: Path = DATA_DIR / "discourse_json"
    VECTOR_STORE_DIR: Path = DATA_DIR / "chroma_db"

    # RAG/LLM config
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o-mini"  # Alternative: gpt-3.5-turbo-0125

    # Optional: Ollama support
    OLLAMA_HOST: str = "http://localhost:11434"

    class Config:
        env_file = ".env"         # ✅ Load env variables from .env
        extra = Extra.allow       # ✅ Allow extra vars


# Singleton settings object
settings = Settings()
