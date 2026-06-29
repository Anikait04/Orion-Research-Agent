from typing import List, Dict, Any, Optional
from autogen_core.tools import FunctionTool
from datetime import datetime


def _format_mla(citation: Dict[str, Any]) -> str:
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    url = citation.get("source_url", "")
    date = citation.get("publication_date", "n.d.")
    retrieval = citation.get("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    if authors:
        author_str = authors[0]
        if len(authors) > 1:
            author_str += " et al."
        author_str += "."
    else:
        author_str = ""

    return f'{author_str} "{title}" Web. {date} <{url}>. Accessed {retrieval}.'


def _format_apa(citation: Dict[str, Any]) -> str:
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    url = citation.get("source_url", "")
    date = citation.get("publication_date", "n.d.")
    retrieval = citation.get("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    if authors:
        author_str = authors[0]
        if len(authors) > 1:
            author_str += " et al."
        author_str += "."
    else:
        author_str = ""

    return f'{author_str} ({date}). {title}. Retrieved {retrieval}, from {url}'


def _format_chicago(citation: Dict[str, Any]) -> str:
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    url = citation.get("source_url", "")
    date = citation.get("publication_date", "n.d.")
    retrieval = citation.get("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    if authors:
        author_str = authors[0]
        if len(authors) > 1:
            author_str += " et al."
        author_str += ". "
    else:
        author_str = ""

    return f'{author_str}"{title}" Accessed {retrieval}. {url}.'


def format_citations(
    citations: List[Dict[str, Any]],
    style: str = "mla",
) -> Dict[str, Any]:
    formatters = {"mla": _format_mla, "apa": _format_apa, "chicago": _format_chicago}
    formatter = formatters.get(style.lower(), _format_mla)

    formatted = [formatter(c) for c in citations]

    seen_urls = set()
    deduplicated = []
    for c, f in zip(citations, formatted):
        if c.get("source_url") not in seen_urls:
            seen_urls.add(c.get("source_url"))
            deduplicated.append(f)

    return {
        "style": style,
        "count": len(deduplicated),
        "citations": deduplicated,
    }


format_citations_tool = FunctionTool(
    func=format_citations,
    description="Format citations in MLA, APA, or Chicago style. Deduplicates by URL. Input: list of {source_url, title, authors, publication_date, retrieval_date}.",
    global_imports=["datetime"],
)
