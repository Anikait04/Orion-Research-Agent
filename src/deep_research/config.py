import os
from dotenv import load_dotenv

load_dotenv()

LLM_CONFIG = {
    "model": os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud"),
    "model_2":os.getenv("OLLAMA_MODEL", "gemma4:cloud"),
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "api_type": "ollama",
}

SEARCH_CONFIG = {
    "search_api_key": os.getenv("SEARCH_API_KEY", ""),
    "search_api_url": os.getenv("SEARCH_API_URL", "https://www.searchapi.io/api/v1/search"),
    "max_results": int(os.getenv("SEARCH_MAX_RESULTS", "10")),
}

RESEARCH_DEFAULTS = {
    "depth": 3,
    "chunk_size": 4000,
    "max_concurrent_tools": 5,
    "max_iterations": 20,
}
