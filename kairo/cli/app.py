import typer
from rich.console import Console

from kairo.agent.controller import AgentController
from kairo.config.settings import Settings
from kairo.storage.database import Database
from kairo.tools.registry import create_default_registry

app: typer.Typer = typer.Typer(help="Kairo developer productivity and academic workflow assistant.")
console: Console = Console()


@app.command()
def chat() -> None:
    """Start a placeholder chat session with Kairo."""
    settings = Settings()
    database = Database(settings.database_path)
    database.initialize()
    controller = AgentController(settings=settings, tool_registry=create_default_registry())
    console.print(controller.start_chat())
