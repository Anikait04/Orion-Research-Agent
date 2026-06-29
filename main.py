import sys
import asyncio
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.deep_research.config import RESEARCH_CONFIG
from src.deep_research.engine import ResearchEngine


async def main():
    engine = ResearchEngine(depth=RESEARCH_CONFIG["depth"])
    report = await engine.run(
        query=RESEARCH_CONFIG["query"],
        output_format=RESEARCH_CONFIG["output_format"],
    )
    print(f"Research complete. Report saved to reports/ directory.")


if __name__ == "__main__":
    asyncio.run(main())
