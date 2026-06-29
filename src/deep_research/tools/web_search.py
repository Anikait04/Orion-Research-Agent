from typing import List, Dict, Any
from autogen_core.tools import FunctionTool
import httpx
from duckduckgo_search import DDGS

def web_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    try:
        return _searchapi_search(query, max_results)
    except Exception:
        return _duckduckgo_search(query, max_results)


def _searchapi_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    import os
    api_key = os.getenv("SEARCH_API_KEY", "")
    api_url = os.getenv("SEARCH_API_URL", "https://www.searchapi.io/api/v1/search")
    if not api_key:
        raise ValueError("SEARCH_API_KEY not set")

    params = {"engine": "google", "q": query, "api_key": api_key, "num": max_results}
    response = httpx.get(api_url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data.get("organic_results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "body": item.get("body", ""),
        })
    return results


def _duckduckgo_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
                "body": r.get("body", ""),
            })
    return results


web_search_tool = FunctionTool(
    func=web_search,
    description="Search the web using SearchAPI.io (primary) or DuckDuckGo (fallback). Returns list of {title, url, snippet, body}.",
    global_imports=["os", "httpx", "duckduckgo_search.DDGS"],
)
