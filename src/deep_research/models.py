from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict


class ResearchQuery(BaseModel):
    query: str
    depth: int = Field(default=3, ge=1, le=5)
    output_format: str = Field(default="markdown", pattern="^(markdown|json)$")


class ResearchPlan(BaseModel):
    original_query: str
    sub_questions: List[str]
    depth: int = 3


class Citation(BaseModel):
    source_url: str
    title: str
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    retrieval_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex[:8])
    topic: str
    claim: str
    evidence: str
    source_urls: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    contradictions: List[str] = Field(default_factory=list)


class ProgressLedger(BaseModel):
    research_query: ResearchQuery
    plan: ResearchPlan
    findings: List[Finding] = Field(default_factory=list)
    completed_sub_questions: List[str] = Field(default_factory=list)
    pending_sub_questions: List[str] = Field(default_factory=list)
    iteration_count: int = 0
    is_complete: bool = False


class ResearchReport(BaseModel):
    query: ResearchQuery
    executive_summary: str = ""
    findings: List[Finding] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    methodology: str = ""
    conclusion: str = ""
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
