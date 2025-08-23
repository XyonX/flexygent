from openai import AsyncOpenAI
from config.config import Config

config = Config()

# Initialize an OpenAI-compatible client for OpenRouter (as per Snyk example:contentReference[oaicite:3]{index=3})
llm_client = AsyncOpenAI(
    base_url=config.openrouter_base_url,       # OpenRouter API base URL
    api_key=config.openrouter_api_key,         # Your OpenRouter API key
    default_headers={"HTTP-Referer": "http://localhost:8000"}  # Required by OpenRouter
)
