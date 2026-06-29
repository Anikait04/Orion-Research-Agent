from typing import List, Dict, Any, Set, Optional
from autogen_core.tools import FunctionTool
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def _get_links_and_content(
    url: str,
    visited: Set[str],
    current_depth: int,
    max_depth: int,
    max_pages: int,
) -> List[Dict[str, Any]]:
    if url in visited or current_depth > max_depth or len(visited) >= max_pages:
        return []

    visited.add(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    text = soup.get_text(separator="\n", strip=True)
    text = "\n".join(line for line in text.splitlines() if line.strip())
    text = text[:5000]

    result = {
        "url": url,
        "title": title,
        "content": text,
        "depth": current_depth,
    }

    results = [result]

    if current_depth < max_depth:
        base_domain = urlparse(url).netloc
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)

            if parsed.netloc and parsed.netloc != base_domain:
                continue
            if parsed.scheme not in ("http", "https"):
                continue

            results.extend(
                _get_links_and_content(
                    full_url, visited, current_depth + 1, max_depth, max_pages
                )
            )

    return results


def crawl_links(seed_urls: List[str], max_depth: int = 2, max_pages: int = 20) -> List[Dict[str, Any]]:
    visited: Set[str] = set()
    all_results = []

    for url in seed_urls:
        if len(visited) >= max_pages:
            break
        all_results.extend(
            _get_links_and_content(url, visited, 0, max_depth, max_pages)
        )

    return all_results


crawl_links_tool = FunctionTool(
    func=crawl_links,
    description="Recursively crawl from seed URLs. Args: seed_urls (list of URLs), max_depth (crawl depth, default 2), max_pages (max pages to visit, default 20). Extracts page title and content from each page. Stays within same domain.",
    global_imports=["httpx", "bs4", "urllib.parse"],
)
