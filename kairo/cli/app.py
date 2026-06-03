import typer
from rich.console import Console

from kairo.agent.controller import AgentController

app: typer.Typer = typer.Typer(help="Kairo developer productivity and academic workflow assistant.")
console: Console = Console()


@app.command()
def chat():

    controller = AgentController()

    print("Kairo started.")

    while True:
        user = input("> ")

        if user == "/repos":
            try:
                tool = controller.registry.get("github_repositories")
                print(tool.execute())
            except KeyError:
                print("No github tool registered.")
            continue

        if user.lower() == "exit":
            break

        response = controller.chat(user)
        print(response)
