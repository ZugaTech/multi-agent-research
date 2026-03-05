import os
from typing import List, Tuple
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from ..models.schemas import ResearchQuery, SearchResult
from ..tools.web_search import search_web, WebSearcher
from ..tools.url_fetcher import URLFetcher, FetchedPage

class SearchAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=0.1)
        self.searcher = WebSearcher()
        self.fetcher = URLFetcher()
        self.tools = [search_web]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a thorough research assistant. Search for comprehensive, authoritative information about the given topic. Prioritize recent sources (last 2 years). Your final answer should just be 'SEARCH_COMPLETE'."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    async def run(self, query: ResearchQuery) -> Tuple[List[SearchResult], List[FetchedPage]]:
        max_results_map = {"quick": 5, "standard": 10, "deep": 20}
        fetch_limit_map = {"quick": 3, "standard": 6, "deep": 10}
        
        num_results = max_results_map.get(query.depth, 10)
        fetch_limit = fetch_limit_map.get(query.depth, 6)
        
        # 1. First, perform search to get the baseline
        raw_results = self.searcher.search(query.topic, num_results=num_results)
        
        # 2. Tell the ReAct agent to find the best ones (optional step for query refinement)
        try:
           await self.agent_executor.ainvoke({"input": f"Topic: {query.topic}. We need up to {num_results} diverse, authoritative links."})
        except Exception as e:
            print(f"[SearchAgent] ReAct agent warning: {e}")
            
        # 3. Fetch the content
        urls_to_fetch = [r.url for r in raw_results[:fetch_limit]]
        fetched_pages = await self.fetcher.fetch_batch(urls_to_fetch)
        
        return raw_results, fetched_pages
