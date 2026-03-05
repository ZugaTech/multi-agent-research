import json
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List
from ..models.schemas import ResearchQuery, SourceSummary, ResearchReport

class ReporterAgent:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        # For the final report, a longer context model is better
        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=0.3)
        self.parser = JsonOutputParser(pydantic_object=ResearchReport)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional research analyst. Synthesize the provided summaries into a comprehensive, well-structured research report.
Write in third person, academic tone. Never fabricate information not present in the summaries.
Always attribute claims to sources using [N] citation style where N is the index of the source.

Your output MUST be a JSON object matching this schema:
{{
    "title": "Report Title",
    "executive_summary": "Max 200 word summary",
    "sections": [
        {{
            "heading": "Section Heading (e.g., Background, Key Findings, Contrasting Viewpoints)",
            "content": "Detailed markdown content with [N] citations. Use multiple paragraphs.",
            "supporting_sources": ["url1", "url2"]
        }}
    ],
    "sources": [
        {{"number": 1, "url": "url", "title": "title", "domain": "domain", "accessed_at": "YYYY-MM-DD"}}
    ],
    "generated_at": "YYYY-MM-DD",
    "word_count": 0
}}

Ensure minimum 800 words total across the sections.
"""),
            ("human", "Topic: {topic}\n\nSummarized Sources (JSON):\n{summaries}")
        ])
        
        self.chain = self.prompt | self.llm | self.parser

    async def run(self, query: ResearchQuery, summaries: List[SourceSummary]) -> ResearchReport:
        # Prepare summaries text
        summaries_dict = [s.model_dump() for s in summaries]
        
        try:
            res = await self.chain.ainvoke({
                "topic": query.topic,
                "summaries": json.dumps(summaries_dict, indent=2)
            })
            
            report = ResearchReport(**res)
            
            # Recalculate word count for accuracy
            total_words = len(report.executive_summary.split())
            for sec in report.sections:
                total_words += len(sec.content.split())
            report.word_count = total_words
            report.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return report
            
        except Exception as e:
            print(f"[ReporterAgent] Failed to generate report: {e}")
            raise
