import typer
from rich.console import Console

from kairo.agent.controller import AgentController
from kairo.config.settings import Settings
from kairo.storage.database import Database
from kairo.tools.registry import create_default_registry

app: typer.Typer = typer.Typer(help="Kairo developer productivity and academic workflow assistant.")
console: Console = Console()


@app.command("chat")
def chat() -> None:
    settings = Settings()
    database = Database(settings.database_path)
    database.initialize()
    controller = AgentController(settings=settings, tool_registry=create_default_registry())
    print(controller.start_chat())