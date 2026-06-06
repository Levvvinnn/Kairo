import typer
from rich.console import Console

from kairo.agent.controller import AgentController

app: typer.Typer = typer.Typer(help="Kairo developer productivity and academic workflow assistant.")
console: Console = Console()


@app.command()
def chat() -> None:

    controller = AgentController()

    console.print(f"[bold cyan]Kairo started.[/bold cyan] Session: {controller.session_id}")

    while True:
        user = input("> ")

        if user.lower() == "exit":
            break

        if user.strip().lower() == "/new":
            session_id = controller.new_session()
            console.print(f"[bold cyan]Kairo[/bold cyan] New session: {session_id}")
            continue

        response = controller.chat(user)

        console.print(response)
