from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from ..models import ResearchReport
from . import ensure_reports_dir, generate_report_filename
from .citation import format_citations

TEMPLATES_DIR = Path(__file__).parent / "templates"


class ReportGenerator:
    def __init__(self, report_dir: Path | None = None):
        self.report_dir = report_dir or ensure_reports_dir()
        self._env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    def generate(self, report: ResearchReport, fmt: str = "markdown") -> str:
        if fmt == "json":
            return self._generate_json(report)
        return self._generate_markdown(report)

    def _generate_markdown(self, report: ResearchReport) -> str:
        template = self._env.get_template("markdown.md.j2")
        formatted_citations = []
        for finding in report.findings:
            for citation in finding.citations:
                formatted_citations.append({
                    "title": citation.title,
                    "source_url": citation.source_url,
                    "authors": citation.authors or [],
                    "publication_date": citation.publication_date or "n.d.",
                    "retrieval_date": citation.retrieval_date,
                })
        citation_result = format_citations(formatted_citations, style="apa")
        return template.render(
            query=report.query.query,
            executive_summary=report.executive_summary,
            findings=report.findings,
            conclusion=report.conclusion,
            methodology=report.methodology,
            citations=citation_result.get("citations", []),
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _generate_json(self, report: ResearchReport) -> str:
        template = self._env.get_template("structured.json.j2")
        return template.render(
            query=report.query.query,
            executive_summary=report.executive_summary,
            findings=[
                {
                    "topic": f.topic,
                    "claim": f.claim,
                    "evidence": f.evidence,
                    "confidence": f.confidence,
                    "citations": [
                        {
                            "title": c.title,
                            "source_url": c.source_url,
                            "authors": c.authors or [],
                        }
                        for c in f.citations
                    ],
                }
                for f in report.findings
            ],
            conclusion=report.conclusion,
            methodology=report.methodology,
            generated_at=datetime.now().isoformat(),
        )

    def save(self, content: str, filename: str | None = None) -> Path:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        filename = filename or generate_report_filename()
        path = self.report_dir / filename
        path.write_text(content, encoding="utf-8")
        return path
