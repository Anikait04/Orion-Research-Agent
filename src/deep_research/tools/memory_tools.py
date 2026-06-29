from typing import Optional
from autogen_core.tools import FunctionTool

from ..memory.chroma_memory import ResearchMemoryStore

_memory_store: ResearchMemoryStore | None = None


def _get_store() -> ResearchMemoryStore:
    global _memory_store
    if _memory_store is None:
        _memory_store = ResearchMemoryStore()
    return _memory_store


async def store_finding(
    topic: str,
    claim: str,
    evidence: str,
    source_url: str = "",
    confidence: float = 0.5,
) -> str:
    store = _get_store()
    await store.store(
        topic=topic,
        content=f"Claim: {claim}\nEvidence: {evidence}",
        source_url=source_url,
        source_type="finding",
        confidence=confidence,
    )
    return f"Stored finding for topic '{topic}' with confidence {confidence}"


async def search_memory(query: str, topic: Optional[str] = None) -> str:
    store = _get_store()
    if topic:
        results = await store.search(topic=topic, query=query)
    else:
        results = await store.search_all(query=query)

    if not results:
        return "No relevant findings found in memory."

    lines = []
    for r in results:
        content = r.content if isinstance(r.content, str) else str(r.content)
        meta = r.metadata or {}
        topic_name = meta.get("topic", "unknown")
        confidence = meta.get("confidence", 0)
        lines.append(f"[{topic_name}] (confidence: {confidence}) {content[:200]}")
    return "\n".join(lines)


store_finding_tool = FunctionTool(
    func=store_finding,
    description="Store a research finding in persistent memory. Args: topic, claim, evidence, source_url, confidence.",
)

search_memory_tool = FunctionTool(
    func=search_memory,
    description="Search memory for relevant findings. Args: query, optional topic filter.",
)
