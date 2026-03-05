import pytest
from unittest.mock import patch
from src.agents.orchestrator import ResearchOrchestrator
from src.models.schemas import ResearchQuery, ResearchReport

@pytest.mark.asyncio
async def test_orchestrator_state_transitions():
    with patch("src.agents.orchestrator.SearchAgent") as mock_sa, \
         patch("src.agents.orchestrator.SummarizerAgent") as mock_sum, \
         patch("src.agents.orchestrator.ReporterAgent") as mock_rep, \
         patch("src.agents.orchestrator.FileWriter") as mock_fw:
         
         # Setup mock returns
         async def mock_search(*args): return [], []
         mock_sa.return_value.run = mock_search
         
         async def mock_summarize(*args): return []
         mock_sum.return_value.run = mock_summarize
         
         async def mock_report(*args): return ResearchReport(title="T", executive_summary="S", sections=[], sources=[], generated_at="now", word_count=0)
         mock_rep.return_value.run = mock_report

         orchestrator = ResearchOrchestrator(api_key="fake")
         query = ResearchQuery(topic="test")
         
         states = []
         async for session in orchestrator.run_pipeline(query):
             states.append(session.status)
             
         assert states == ["initialized", "searching", "summarizing", "reporting", "completed"]
         assert orchestrator.sessions[session.session_id].report is not None
