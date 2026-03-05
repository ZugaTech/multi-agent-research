# Multi-Agent Research Assistant 🧠📚

A, production-ready research orchestration system built with LangChain, FastAPI and Typer. It deploys three specialized AI agents to automate the tedious process of searching, reading, synthesizing and formatting deep research on any topic.

## The Agents

1. **Agent 1: The Searcher (ReAct)**
 - Autonomously determines the best search queries.
 - Uses DuckDuckGo (or SerpApi) to find relevant, recent sources.
 - Fetches and cleans HTML from the live web using asynchronous HTTP requests.

2. **Agent 2: The Analyst**
 - Reads each source independently and in parallel.
 - Extracts structured facts (JSON) including key points, relevant quotes and calculates a credibility score.

3. **Agent 3: The Writer**
 - Synthesizes the extracted facts into a cohesive, academic report.
 - Formats the output with embedded citations and an executive summary.
 - Exports directly to Markdown and styled PDF using ReportLab.

## Quickstart

### Prerequisites
```bash
pip install -r requirements.txt
# Or if using pyproject.toml:
pip install.
```

Configure your environment in `.env`:
```env
OPENAI_API_KEY=sk-...
SERPAPI_KEY=... # Optional, falls back to DuckDuckGo
```

### CLI Mode
Run a research task directly from the terminal with live rich progress rendering:
```bash
# Quick research (fetches 3 sources)
python -m src.main run "Impact of Quantum Computing on Cryptography" --depth quick

# Deep research (fetches 10 sources, outputs Markdown and PDF)
python -m src.main run "History of the Byzantine Empire" --depth deep --output both
```

### Server / Web UI Mode
Start the FastAPI backend:
```bash
python -m src.main serve --port 8000
```
Then, open `frontend/index.html` in your browser for a clean, interactive user interface that streams progress live via Server-Sent Events (SSE).

## Outputs
All generated session data and final reports are saved in the `output/` directory.

## Tests
To run the automated test suite (with mocked web searching):
```bash
pytest tests/
```