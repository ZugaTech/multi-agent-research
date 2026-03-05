import os
import uuid
import json
import time
from datetime import datetime
from typing import AsyncGenerator
from ..models.schemas import ResearchQuery, ResearchSession, ResearchReport
from .search_agent import SearchAgent
from .summarizer_agent import SummarizerAgent
from .reporter_agent import ReporterAgent
from ..tools.file_writer import FileWriter

class ResearchOrchestrator:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.search_agent = SearchAgent(api_key, model)
        self.summarizer_agent = SummarizerAgent(api_key, model)
        self.reporter_agent = ReporterAgent(api_key, model)
        self.sessions: dict[str, ResearchSession] = {}
        os.makedirs("output", exist_ok=True)

    def _save_session(self, session: ResearchSession):
        path = f"output/{session.session_id}.json"
        with open(path, "w") as f:
            f.write(session.model_dump_json(indent=2))

    async def run_pipeline(self, query: ResearchQuery) -> AsyncGenerator[ResearchSession, None]:
        session_id = str(uuid.uuid4())
        session = ResearchSession(
            session_id=session_id,
            query=query,
            started_at=datetime.now().isoformat()
        )
        self.sessions[session_id] = session
        self._save_session(session)
        yield session

        try:
            # 1. Search Phase
            session.status = "searching"
            yield session
            start_search = time.time()
            raw_results, fetched_pages = await self.search_agent.run(query)
            session.search_results = raw_results
            self._save_session(session)

            # 2. Summarization Phase
            session.status = "summarizing"
            yield session
            summaries = await self.summarizer_agent.run(fetched_pages)
            session.summaries = summaries
            self._save_session(session)

            # 3. Reporting Phase
            session.status = "reporting"
            yield session
            report = await self.reporter_agent.run(query, summaries)
            session.report = report
            
            # File Writing
            base_filename = f"output/{session_id}_report"
            if query.output_format in ["markdown", "both"]:
                FileWriter.write_markdown(report, f"{base_filename}.md")
            if query.output_format in ["pdf", "both"]:
                FileWriter.write_pdf(report, f"{base_filename}.pdf")

            # Finalize
            session.status = "completed"
            session.finished_at = datetime.now().isoformat()
            self._save_session(session)
            yield session

        except Exception as e:
            session.status = "failed"
            session.finished_at = datetime.now().isoformat()
            self._save_session(session)
            print(f"[Orchestrator] Pipeline failed: {e}")
            yield session
