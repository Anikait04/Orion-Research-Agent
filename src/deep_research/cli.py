import argparse
import sys
from dataclasses import dataclass
from .config import RESEARCH_DEFAULTS
from .models import ResearchQuery


@dataclass
class CLIArgs:
    query: ResearchQuery
    output_path: str = f"/reports"
    session_id: str = ""


def parse_args(args: list[str] | None = None) -> CLIArgs:
    parser = argparse.ArgumentParser(
        description="Deep Research Agent - AI-powered multi-agent research assistant"
    )
    parser.add_argument("query", type=str, nargs="?", help="Research query")
    parser.add_argument("--depth", type=int, default=RESEARCH_DEFAULTS["depth"], choices=range(1, 6),
                        help="Research depth (1-5, default: 3)")
    parser.add_argument("--format", dest="output_format", choices=["markdown", "json"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--output", "-o", type=str, default="",
                        help="Save output to file")
    parser.add_argument("--list-sessions", action="store_true",
                        help="List saved research sessions")
    parser.add_argument("--session", type=str, default="",
                        help="Resume a previous session")

    parsed = parser.parse_args(args)

    if parsed.list_sessions:
        from .memory import list_sessions
        sessions = list_sessions()
        if not sessions:
            print("No saved sessions found.")
        else:
            print(f"{'Session ID':<25} {'Query':<50} {'Status':<15} {'Date':<25}")
            print("-" * 115)
            for s in sessions:
                print(f"{s.session_id:<25} {s.query[:48]:<50} {s.status:<15} {s.created_at[:19]:<25}")
        sys.exit(0)

    if not parsed.query:
        parser.print_help()
        sys.exit(1)

    research_query = ResearchQuery(
        query=parsed.query,
        depth=parsed.depth,
        output_format=parsed.output_format,
    )

    return CLIArgs(
        query=research_query,
        output_path=parsed.output,
        session_id=parsed.session,
    )
