from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class ResearchQuery(BaseModel):
    topic: str
    depth: Literal["quick", "standard", "deep"] = "standard"
    max_sources: int = 5
    output_format: Literal["markdown", "pdf", "both"] = "both"

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    source_domain: str
    fetched_at: str

class SourceSummary(BaseModel):
    url: str
    title: str
    key_points: List[str] = Field(description="3-7 key factual claims with sources")
    relevant_quotes: List[str] = Field(description="2-3 direct, short relevant quotes")
    credibility_score: float = Field(description="0 to 1 score based on source quality")
    date_published: Optional[str] = None

class ReportSection(BaseModel):
    heading: str
    content: str
    supporting_sources: List[str]

class Citation(BaseModel):
    number: int
    url: str
    title: str
    domain: str
    accessed_at: str

class ResearchReport(BaseModel):
    title: str
    executive_summary: str
    sections: List[ReportSection]
    sources: List[Citation]
    generated_at: str
    word_count: int

class ResearchSession(BaseModel):
    session_id: str
    query: ResearchQuery
    status: Literal["initialized", "searching", "summarizing", "reporting", "completed", "failed"] = "initialized"
    search_results: List[SearchResult] = []
    summaries: List[SourceSummary] = []
    report: Optional[ResearchReport] = None
    started_at: str
    finished_at: Optional[str] = None
    token_usage: int = 0
