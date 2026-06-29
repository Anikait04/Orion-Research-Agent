from typing import List, Dict, Any
from autogen_core.tools import FunctionTool
from difflib import SequenceMatcher


DOMAIN_AUTHORITY = {
    "arxiv.org": 0.8,
    "scholar.google.com": 0.8,
    "edu": 0.7,
    "gov": 0.7,
    "wikipedia.org": 0.5,
    "medium.com": 0.3,
    "blogspot.com": 0.2,
}


def _domain_authority(url: str) -> float:
    for domain, score in DOMAIN_AUTHORITY.items():
        if domain in url:
            return score
    return 0.4


def _compute_confidence(
    source_count: int,
    recency_days: float,
    domain_score: float,
) -> float:
    confidence = 0.3
    confidence += min(source_count * 0.15, 0.4)
    confidence += max(0.1 - (recency_days / 3650), 0) * 0.15
    confidence += domain_score * 0.15
    return round(min(confidence, 1.0), 2)


def verify_source(
    claims: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results = []

    for claim in claims:
        claim_text = claim.get("claim", "").lower()
        matching_sources = []
        contradictions = []

        for source in sources:
            content = (source.get("title", "") + " " + source.get("body", "")).lower()
            if claim_text in content or any(
                word in content for word in claim_text.split() if len(word) > 4
            ):
                matching_sources.append(source)

            if "however" in content or "contrary" in content:
                contradictions.append(source.get("url", ""))

        source_count = len(matching_sources)
        recency = 365
        domain_score = (
            max(_domain_authority(s.get("url", "")) for s in matching_sources)
            if matching_sources
            else 0.3
        )

        confidence = _compute_confidence(source_count, recency, domain_score)

        results.append({
            "claim": claim.get("claim", ""),
            "confidence": confidence,
            "source_count": source_count,
            "matching_sources": [s.get("url", "") for s in matching_sources],
            "contradictions": contradictions,
            "assessment": _assess(confidence, contradictions),
        })

    return results


def _assess(confidence: float, contradictions: List[str]) -> str:
    if contradictions:
        return "contradictory"
    if confidence >= 0.7:
        return "well-supported"
    if confidence >= 0.4:
        return "partially-supported"
    return "insufficient-evidence"


verify_source_tool = FunctionTool(
    func=verify_source,
    description="Cross-reference claims against sources, assign confidence scores, and flag contradictions. Input: list of claims {claim}, list of sources {title, url, body}.",
    global_imports=["difflib"],
)
