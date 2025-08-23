
from pydantic_settings import BaseSettings  # ✅ correct for v2

class Config(BaseSettings):
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    chroma_db_path: str = "chroma_data"

    class Config:
        env_file = ".env"  # Load variables from a .env file
