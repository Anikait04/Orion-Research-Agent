import os
from dotenv import load_dotenv

load_dotenv()

LLM_CONFIG = {
    "model": os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud"),
    "model_2": os.getenv("OLLAMA_MODEL", "gemma4:cloud"),
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

RESEARCH_CONFIG = {
    "query": "can you please compare iphone 17 pro max and nokia 3310 and tell me which one should i buy",
    "depth": 3,
    "output_format": "markdown",
    "output_dir": "reports",
}

DEPTH_CONFIG = {
    1: {"sub_questions": 2, "crawl_depth": 1, "max_pages": 10, "max_iterations": 10},
    2: {"sub_questions": 3, "crawl_depth": 1, "max_pages": 15, "max_iterations": 15},
    3: {"sub_questions": 4, "crawl_depth": 2, "max_pages": 20, "max_iterations": 20},
    4: {"sub_questions": 5, "crawl_depth": 2, "max_pages": 30, "max_iterations": 30},
    5: {"sub_questions": 6, "crawl_depth": 3, "max_pages": 40, "max_iterations": 40},
}
