import sys
import asyncio
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.deep_research.cli import parse_args
from src.deep_research.engine import ResearchEngine


async def main():
    cli_args = parse_args()
    engine = ResearchEngine(depth=cli_args.query.depth)
    report = await engine.run(cli_args.query.query, output_format=cli_args.query.output_format)

    if cli_args.query.output_format == "json":
        output = report.model_dump_json(indent=2)
    else:
        output = f"# {cli_args.query.query}\n\n"
        output += f"## Executive Summary\n{report.executive_summary}\n\n"
        for f in report.findings:
            output += f"## {f.claim}\n{f.evidence}\n"
            if f.citations:
                output += "### Sources\n"
                for c in f.citations:
                    output += f"- [{c.title}]({c.source_url})\n"
            output += "\n"
        if report.conclusion:
            output += f"## Conclusion\n{report.conclusion}\n"

    print(output)

    if cli_args.output_path:
        os.makedirs(os.path.dirname(cli_args.output_path) or ".", exist_ok=True)
        with open(cli_args.output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nReport saved to: {cli_args.output_path}")


if __name__ == "__main__":
    asyncio.run(main())
