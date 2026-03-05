import os
import asyncio
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from ..models.schemas import ResearchQuery
from ..agents.orchestrator import ResearchOrchestrator

router = APIRouter()
orchestrator = ResearchOrchestrator(api_key=os.getenv("OPENAI_API_KEY", ""))

@router.post("/research/stream")
async def stream_research(query: ResearchQuery):
    async def event_generator():
        try:
            async for session in orchestrator.run_pipeline(query):
                yield {
                    "event": "update",
                    "data": session.model_dump_json()
                }
        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }
            
    return EventSourceResponse(event_generator())

@router.get("/research/sessions/{session_id}")
async def get_session(session_id: str):
    session = orchestrator.sessions.get(session_id)
    if not session:
        # Try loading from disk
        path = f"output/{session_id}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        raise HTTPException(status_code=404, detail="Session not found")
    return session
