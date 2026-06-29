from typing import List, Dict, Any
from autogen_core.tools import FunctionTool
import arxiv


def arxiv_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    results = []
    for paper in client.results(search):
        results.append({
            "id": paper.entry_id,
            "title": paper.title,
            "authors": [a.name for a in paper.authors],
            "published": paper.published.strftime("%Y-%m-%d") if paper.published else "",
            "updated": paper.updated.strftime("%Y-%m-%d") if paper.updated else "",
            "summary": paper.summary,
            "pdf_url": paper.pdf_url,
            "links": [{"href": str(l), "title": l.title, "rel": l.rel} for l in paper.links],
            "primary_category": str(paper.primary_category),
            "categories": list(paper.categories),
        })

    return results


arxiv_search_tool = FunctionTool(
    func=arxiv_search,
    description="Search academic papers on Arxiv. Returns list of papers with title, authors, abstract, and PDF URL.",
    global_imports=["arxiv"],
)
