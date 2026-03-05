import pytest
from unittest.mock import patch, MagicMock
from src.agents.search_agent import SearchAgent
from src.models.schemas import ResearchQuery, SearchResult

@pytest.fixture
def mock_searcher():
    with patch("src.agents.search_agent.WebSearcher") as mock:
        instance = mock.return_value
        instance.search.return_value = [
            SearchResult(url="http://test.com/1", title="Test 1", snippet="Snippet 1", source_domain="test.com", fetched_at="2025-01-01")
        ]
        yield mock

@pytest.fixture
def mock_fetcher():
    with patch("src.agents.search_agent.URLFetcher") as mock:
        instance = mock.return_value
        instance.fetch_batch.return_value = [] # AsyncMock behavior handled below
        yield mock

@pytest.mark.asyncio
async def test_search_agent_flow(mock_searcher, mock_fetcher):
    with patch("src.agents.search_agent.ChatOpenAI"):
        with patch("src.agents.search_agent.create_tool_calling_agent"):
            agent = SearchAgent(api_key="fake")
            
            # Setup async return for fetch_batch
            async def mock_batch(*args): return []
            agent.fetcher.fetch_batch = mock_batch
            
            # Setup async return for ReAct agent
            async def mock_ainvoke(*args, **kwargs): return {"output": "SEARCH_COMPLETE"}
            agent.agent_executor.ainvoke = mock_ainvoke

            query = ResearchQuery(topic="test", depth="quick")
            raw, fetched = await agent.run(query)

            assert len(raw) == 1
            assert raw[0].title == "Test 1"
