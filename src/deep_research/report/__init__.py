from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "reports"


def ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR


def generate_report_filename() -> str:
    return f"reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


__all__ = ["REPORTS_DIR", "ensure_reports_dir", "generate_report_filename"]
