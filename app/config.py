#app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Extra

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = None
    USE_OPENAI: bool = True  # True = use OpenAI, False = use Ollama

    DATA_DIR: Path = BASE_DIR / "data"
    DISCOURSE_JSON_DIR: Path = DATA_DIR / "discourse_json"
    VECTOR_STORE_DIR: Path = DATA_DIR / "chroma_db"

    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"  # Railway uses OpenAI for public

    class Config:
        env_file = ".env"
        extra = Extra.allow

settings = Settings()
