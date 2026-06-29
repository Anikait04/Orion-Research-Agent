from datetime import datetime
from typing import Any


def _format_mla(citation: dict[str, Any]) -> str:
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    url = citation.get("source_url", "")
    pub_date = citation.get("publication_date", "n.d.")
    retrieval = citation.get("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    if authors:
        author_str = authors[0]
        if len(authors) > 1:
            author_str += " et al."
        author_str += "."
    else:
        author_str = ""

    return f'{author_str} "{title}" Web. {pub_date} <{url}>. Accessed {retrieval}.'


def _format_apa(citation: dict[str, Any]) -> str:
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    url = citation.get("source_url", "")
    pub_date = citation.get("publication_date", "n.d.")
    retrieval = citation.get("retrieval_date", datetime.now().strftime("%Y-%m-%d"))

    if authors:
        author_str = authors[0]
        if len(authors) > 1:
            author_str += " et al."
        author_str += "."
    else:
        author_str = ""

    return f'{author_str} ({pub_date}). {title}. Retrieved {retrieval}, from {url}'


def _format_chicago(citation: dict[str, Any]) -> str:
    authors = citation.get("authors", [])
    title = citation.get("title", "Untitled")
    url = citation.get("source_url", "")
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
    citations: list[dict[str, Any]],
    style: str = "mla",
) -> dict[str, Any]:
    formatters = {"mla": _format_mla, "apa": _format_apa, "chicago": _format_chicago}
    formatter = formatters.get(style.lower(), _format_mla)

    formatted = [formatter(c) for c in citations]

    seen_urls: set[str] = set()
    deduplicated: list[str] = []
    for c, f in zip(citations, formatted):
        if c.get("source_url") not in seen_urls:
            seen_urls.add(c.get("source_url", ""))
            deduplicated.append(f)

    return {
        "style": style,
        "count": len(deduplicated),
        "citations": deduplicated,
    }
