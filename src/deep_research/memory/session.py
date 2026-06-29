from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import json
import os

from ..models import ResearchQuery, ResearchPlan, Finding, Citation, ProgressLedger, ResearchReport


class ResearchSession(BaseModel):
    session_id: str = Field(default_factory=lambda: datetime.now().strftime("ses_%Y%m%d_%H%M%S"))
    query: str
    depth: int = 3
    output_format: str = "markdown"
    status: str = "in_progress"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    findings_count: int = 0
    filepath: Optional[str] = None


SESSIONS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "sessions"


def _ensure_sessions_dir() -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return SESSIONS_DIR


def save_session(session: ResearchSession) -> str:
    _ensure_sessions_dir()
    path = SESSIONS_DIR / f"{session.session_id}.json"
    session.filepath = str(path.resolve())
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.model_dump(), f, indent=2, ensure_ascii=False)
    return session.filepath


def load_session(session_id: str) -> ResearchSession:
    path = get_session_path(session_id)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ResearchSession(**data)


def list_sessions() -> List[ResearchSession]:
    if not SESSIONS_DIR.exists():
        return []
    sessions = []
    for fp in sorted(SESSIONS_DIR.iterdir(), reverse=True):
        if fp.suffix == ".json":
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            sessions.append(ResearchSession(**data))
    sessions.sort(key=lambda s: s.created_at, reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    path = get_session_path(session_id)
    if path.exists():
        path.unlink()
        return True
    return False


def get_session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"
