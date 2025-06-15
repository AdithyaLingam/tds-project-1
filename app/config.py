from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Extra

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # AI Proxy token stored as OPENAI_API_KEY
    OPENAI_API_KEY: str | None = None
    RAW_COOKIE_STRING: str

    # Whether to use OpenAI-compatible endpoints (True = AI Proxy)
    USE_OPENAI: bool = True

    # Data directories
    DATA_DIR: Path = BASE_DIR / "data"
    DISCOURSE_JSON_DIR: Path = DATA_DIR / "discourse_json"
    VECTOR_STORE_DIR: Path = DATA_DIR / "chroma_db"

    # HuggingFace-compatible embedding model via AI Proxy
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Chat model via AI Proxy
    LLM_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"
        extra = Extra.allow  # allow RAW_COOKIE_STRING and other extras

settings = Settings()
