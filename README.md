# Orion Research Agent

An AI-powered multi-agent research system that autonomously investigates topics, gathers information from multiple sources, cross-references findings, and produces structured reports with citations.

## What It Does

Orion takes a research query and orchestrates a team of specialized AI agents that work together to produce a comprehensive report. Each agent handles a specific part of the research pipeline — from searching the web and extracting content to verifying sources and synthesizing the final output.

The system is designed for depth. A configurable research depth parameter (1-5) controls how many sub-questions are explored, how deep the web crawler goes, and how many pages are examined per session.

## Architecture

The system is built on Microsoft's AutoGen framework using a `SelectorGroupChat` pattern, where an orchestrator agent dynamically delegates tasks to specialized agents based on the current research state.

### Agent Team

| Agent | Role |
|-------|------|
| **ResearchOrchestrator** | Coordinates the workflow, tracks progress, decides which agent acts next, and signals completion |
| **SearchSpecialist** | Formulates queries, searches across web and academic databases, triages results by relevance |
| **DeepExtractor** | Scrapes full page content from URLs and extracts text from PDF documents |
| **ResearchAnalyst** | Cross-references claims across sources, assigns confidence scores, flags contradictions |
| **ReportSynthesizer** | Compiles all findings into a structured report with proper citations |
| **ResearchMemory** | Stores and retrieves findings from a persistent vector database for cross-session recall |

### Tools

| Tool | Purpose |
|------|---------|
| Web Search | SearchAPI.io (primary) with DuckDuckGo fallback |
| Arxiv Search | Academic paper search with abstracts and PDF links |
| Web Scraper | Single-page content extraction with boilerplate removal |
| PDF Extractor | Download and extract text from PDF files |
| Crawl Links | Recursive same-domain crawling with configurable depth |
| Citation Formatter | MLA, APA, and Chicago citation styles with deduplication |
| Source Verifier | Claim cross-referencing, confidence scoring, and contradiction detection |
| Memory Store | Persistent ChromaDB-backed vector storage for research findings |

## Report Generation

Reports are generated using Jinja2 templates and saved to a dedicated `reports/` directory. Each report is automatically timestamped to prevent overwrites and enable chronological sorting.

Reports include an executive summary, detailed findings with source citations, methodology notes, and a conclusion. Both Markdown and JSON output formats are supported.

## Memory System

The research memory is built on ChromaDB, providing persistent vector storage across sessions. Before starting a new research run, the system checks memory for existing relevant findings. During and after research, new findings are stored for future retrieval. Each research topic gets its own ChromaDB collection for organized querying.

## Depth Control

The research depth parameter (1-5) directly influences behavior:

| Depth | Sub-questions | Crawl depth | Max pages | Max iterations |
|-------|---------------|-------------|-----------|----------------|
| 1 | 2 | 1 | 10 | 10 |
| 2 | 3 | 1 | 15 | 15 |
| 3 | 4 | 2 | 20 | 20 |
| 4 | 5 | 2 | 30 | 30 |
| 5 | 6 | 3 | 40 | 40 |

Higher depth means more sub-questions are generated, the crawler explores deeper link chains, and more pages are examined overall.

## Session Management

Every research run is saved as a session with metadata including the query, depth, output format, status, and timestamps. Sessions are stored as JSON files and can be listed or resumed later.

## Project Structure

```
src/deep_research/
├── config.py              # LLM, search, and research configuration
├── models.py              # Pydantic data models
├── engine.py              # Core research engine orchestrating the workflow
├── cli.py                 # Command-line interface (optional override layer)
├── tools/                 # FunctionTool implementations for all research tools
├── agents/                # Agent definitions with system prompts and tool bindings
├── memory/                # ChromaDB vector store and session persistence
└── report/                # Report generation with Jinja2 templates
```

## Tech Stack

- **Framework**: AutoGen AgentChat (multi-agent orchestration)
- **LLM Backend**: Ollama (local inference)
- **Vector Store**: ChromaDB (persistent memory)
- **Web Access**: httpx + BeautifulSoup (scraping), DuckDuckGo + SearchAPI (search)
- **Academic Search**: Arxiv API
- **PDF Processing**: pdfplumber
- **Templating**: Jinja2
- **Data Models**: Pydantic v2
