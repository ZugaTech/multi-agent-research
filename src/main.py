import os
import typer
import asyncio
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from .models.schemas import ResearchQuery
from .agents.orchestrator import ResearchOrchestrator

app = typer.Typer(help="Multi-Agent Research Assistant")
console = Console()

@app.command()
def serve(port: int = 8000):
    """Start the FastAPI server for the Web UI."""
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=True)

@app.command()
def run(
    topic: str,
    depth: str = typer.Option("standard", help="quick, standard, or deep"),
    output: str = typer.Option("both", help="markdown, pdf, or both")
):
    """Run a research query from the CLI."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set.[/red]")
        raise typer.Exit(1)
        
    query = ResearchQuery(topic=topic, depth=depth, output_format=output)
    orchestrator = ResearchOrchestrator(api_key=api_key)
    
    async def execute():
        current_status = "initialized"
        
        with Live(Panel("Initializing agents...", title=f"Researching: {topic}"), refresh_per_second=4) as live:
            async for session in orchestrator.run_pipeline(query):
                if session.status != current_status:
                    current_status = session.status
                    
                    if current_status == "searching":
                        text = Text("🔍 Agent 1 (Searcher) is scouring the web...", style="cyan")
                    elif current_status == "summarizing":
                        text = Text(f"🧠 Agent 2 (Analyst) is reading and summarizing {len(session.search_results)} sources...", style="magenta")
                    elif current_status == "reporting":
                        text = Text("📝 Agent 3 (Writer) is compiling the final report...", style="yellow")
                    elif current_status == "completed":
                        text = Text("✅ Research complete!", style="green")
                    elif current_status == "failed":
                        text = Text("❌ Research failed.", style="red")
                    else:
                        text = Text(f"Status: {current_status}")
                        
                    live.update(Panel(text, title=f"Researching: {topic}"))
                    
            if session.report:
                console.print(f"\n[bold green]Report saved to output/{session.session_id}_report.md/pdf[/bold green]")
                console.print(f"\n[cyan]Executive Summary:[/cyan]\n {session.report.executive_summary}\n")

    asyncio.run(execute())

if __name__ == "__main__":
    app()
