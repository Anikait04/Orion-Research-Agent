import re
from datetime import date

from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from autogen_core.memory import MemoryContent, MemoryMimeType

from ..models import Finding


class ResearchMemoryStore:
    """Persistent ChromaDB-backed memory store for research findings.

    Uses a dedicated collection per topic for organized retrieval.
    Metadata schema: {topic, source_url, source_type, confidence, retrieval_date}
    """

    def __init__(self, persistence_path: str = ".chromadb", score_threshold: float = 0.1, k: int = 10):
        self._persistence_path = persistence_path
        self._score_threshold = score_threshold
        self._k = k
        self._memories: dict[str, ChromaDBVectorMemory] = {}
        self._topic_names: set[str] = set()

    def _sanitize_collection_name(self, name: str) -> str:
        name = name.lower()
        name = re.sub(r"[^a-z0-9-]", "-", name)
        name = re.sub(r"-+", "-", name)
        name = name.strip("-")
        return name[:63]

    def _get_memory(self, topic: str) -> ChromaDBVectorMemory:
        if topic not in self._memories:
            collection_name = self._sanitize_collection_name(topic)
            config = PersistentChromaDBVectorMemoryConfig(
                persistence_path=self._persistence_path,
                collection_name=collection_name,
                k=self._k,
                score_threshold=self._score_threshold,
                allow_reset=True,
            )
            self._memories[topic] = ChromaDBVectorMemory(config=config)
            self._topic_names.add(topic)
        return self._memories[topic]

    async def store(self, topic: str, content: str, source_url: str = "", source_type: str = "web", confidence: float = 0.5) -> None:
        memory = self._get_memory(topic)
        metadata = {
            "topic": topic,
            "source_url": source_url,
            "source_type": source_type,
            "confidence": confidence,
            "retrieval_date": date.today().isoformat(),
        }
        mc = MemoryContent(content=content, mime_type=MemoryMimeType.TEXT, metadata=metadata)
        await memory.add(mc)

    async def store_finding(self, finding: Finding) -> None:
        source_url = finding.source_urls[0] if finding.source_urls else ""
        await self.store(
            topic=finding.topic,
            content=finding.model_dump_json(),
            source_url=source_url,
            source_type="finding",
            confidence=finding.confidence,
        )

    async def search(self, topic: str, query: str, k: int | None = None) -> list[MemoryContent]:
        if topic not in self._memories and topic not in self._topic_names:
            return []
        memory = self._get_memory(topic)
        result = await memory.query(query=query)
        return result.results

    async def search_all(self, query: str, k: int = 5) -> list[MemoryContent]:
        all_results: list[MemoryContent] = []
        for topic in list(self._topic_names):
            try:
                results = await self.search(topic, query, k=k)
                all_results.extend(results)
            except Exception:
                continue
        all_results.sort(key=lambda x: x.metadata.get("confidence", 0) if x.metadata else 0, reverse=True)
        return all_results[:k]

    async def get_findings(self, topic: str, k: int = 100) -> list[Finding]:
        if topic not in self._memories and topic not in self._topic_names:
            self._get_memory(topic)
        collection_name = self._sanitize_collection_name(topic)
        query_mem = ChromaDBVectorMemory(config=PersistentChromaDBVectorMemoryConfig(
            persistence_path=self._persistence_path,
            collection_name=collection_name,
            k=k,
            score_threshold=0.0,
            allow_reset=True,
        ))
        result = await query_mem.query(query="")
        await query_mem.close()
        findings = []
        for item in result.results:
            try:
                findings.append(Finding.model_validate_json(item.content))
            except Exception:
                continue
        return findings

    async def delete_topic(self, topic: str) -> None:
        if topic in self._memories:
            await self._memories[topic].clear()
            del self._memories[topic]
            self._topic_names.discard(topic)

    async def close(self) -> None:
        for memory in self._memories.values():
            try:
                await memory.close()
            except Exception:
                continue
        self._memories.clear()
        self._topic_names.clear()
