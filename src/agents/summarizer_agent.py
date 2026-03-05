import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from ..models.schemas import SourceSummary
from ..tools.url_fetcher import FetchedPage

class SummarizerAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=0.1)
        self.parser = JsonOutputParser(pydantic_object=SourceSummary)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert intelligence analyst. Process the provided webpage content and extract a structured summary.
Your output MUST be a JSON object matching this schema:
{{
    "url": "string (provided url)",
    "title": "string (provided title)",
    "key_points": ["fact 1", "fact 2", ... (3-7 points)],
    "relevant_quotes": ["quote 1", "quote 2", ... (2-3 short direct quotes)],
    "credibility_score": float (0.0 to 1.0, based on traits like author, date, domain (.edu/.gov higher), external citations),
    "date_published": "YYYY-MM-DD or null if not found"
}}
Never fabricate information. Provide only JSON output without markdown fences if possible.
"""),
            ("human", "Title: {title}\nURL: {url}\n\nContent:\n{content}")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def _summarize_single(self, page: FetchedPage) -> SourceSummary:
        try:
            res = await self.chain.ainvoke({
                "title": page.title,
                "url": page.url,
                "content": page.text
            })
            # Ensure URL and title are propagated correctly
            res['url'] = page.url
            res['title'] = page.title
            return SourceSummary(**res)
        except Exception as e:
            print(f"[SummarizerAgent] Failed to summarize {page.url}: {e}")
            return SourceSummary(url=page.url, title=page.title, key_points=["Error generating summary"], relevant_quotes=[], credibility_score=0.1)

    async def run(self, pages: List[FetchedPage]) -> List[SourceSummary]:
        tasks = [self._summarize_single(page) for page in pages]
        summaries = await asyncio.gather(*tasks)
        return list(summaries)
