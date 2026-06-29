from typing import Dict, Any
from autogen_core.tools import FunctionTool
import httpx
from bs4 import BeautifulSoup


def web_scraper(url: str, max_chars: int = 10000) -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    text = soup.get_text(separator="\n", strip=True)
    text = "\n".join(line for line in text.splitlines() if line.strip())

    if len(text) > max_chars:
        text = text[:max_chars] + "..."

    return {
        "url": url,
        "title": title,
        "content": text,
        "content_length": len(text),
    }


web_scraper_tool = FunctionTool(
    func=web_scraper,
    description="Extract the main text content from a webpage URL. Returns title, content, and content length.",
    global_imports=["httpx", "bs4"],
)
