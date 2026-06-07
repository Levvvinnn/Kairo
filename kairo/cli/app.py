import typer
from rich.console import Console

from kairo.agent.controller import AgentController
from kairo.auth.google_oauth import run_oauth_flow as run_google_oauth
from kairo.integrations.canvas_client import CanvasClient
from kairo.storage.oauth_store import TokenStore
from kairo.tools.registry import create_default_registry
from kairo.storage.database import Database
from kairo.config.settings import settings
from rich.table import Table
from rich.panel import Panel
from rich import box


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


@app.command("auth-google")
def auth_google() -> None:
    """Perform Google OAuth interactive authentication and store tokens."""
    console.print(Panel("Starting Google OAuth flow...", title="Kairo"))
    token = run_google_oauth("google")
    subtitle = None
    try:
        if token and isinstance(token, dict):
            exp = token.get("expires_at")
            if exp is not None:
                subtitle = str(exp)
    except Exception:
        subtitle = None

    console.print(Panel("Google authentication complete.", title="Kairo", subtitle=subtitle))


@app.command("auth-canvas")
def auth_canvas() -> None:
    """Prompt for Canvas base URL and API token and validate them."""
    base = typer.prompt("Canvas base URL (e.g. https://canvas.instructure.com)")
    api_token = typer.prompt("Canvas API token", hide_input=True)
    client = CanvasClient(base_url=base, token=api_token)
    try:
        courses = client.get_courses()
        store = TokenStore()
        store.save_token("canvas", {"base_url": base, "api_token": api_token})
        console.print(Panel(f"Canvas validated. {len(courses)} courses found.", title="Kairo"))
    except Exception as exc:
        console.print(Panel(f"Canvas validation failed: {exc}", title="Kairo"))


@app.command("status")
def status() -> None:
    """Show connection status, session info, and tool availability."""
    db = Database(settings.database_path)
    session = db.get_or_create_latest_session()
    messages = db.list_messages(session.id)
    tools = create_default_registry().list_tools()

    table = Table(title="Kairo Status", box=box.SIMPLE)
    table.add_column("Connection")
    table.add_column("Status")

    # Connections
    store = TokenStore()
    gh = "OK" if settings.github_token else "Missing"
    google = "Connected" if store.get_token("google") else "Missing"
    canvas = "Connected" if store.get_token("canvas") else "Missing"
    table.add_row("GitHub", gh)
    table.add_row("Google", google)
    table.add_row("Canvas", canvas)

    console.print(table)

    sess_table = Table(title="Session", box=box.SIMPLE)
    sess_table.add_column("Session ID")
    sess_table.add_column("Messages")
    sess_table.add_column("Tool Calls")
    tool_calls = db.list_tool_calls(session.id)
    sess_table.add_row(str(session.id), str(len(messages)), str(len(tool_calls)))
    console.print(sess_table)

    tools_table = Table(title="Tools", box=box.SIMPLE)
    tools_table.add_column("Tool")
    tools_table.add_column("Available")
    for t in sorted(tools):
        tools_table.add_row(t, "Yes")
    console.print(tools_table)


@app.command("setup")
def setup() -> None:
    """Interactive setup wizard guiding through required auth and keys."""
    checks = {
        "Gemini": bool(settings.gemini_api_key or settings.openai_api_key),
        "GitHub": bool(settings.github_token),
        "Google": bool(TokenStore().get_token("google")),
        "Canvas": bool(TokenStore().get_token("canvas")),
    }

    for name, ok in checks.items():
        console.print(f"[{'green' if ok else 'red'}]{'✓' if ok else ' ' }[/] {name}")

    if not checks["Google"]:
        if typer.confirm("Run Google OAuth now?"):
            auth_google()

    if not checks["Canvas"]:
        if typer.confirm("Configure Canvas now?"):
            auth_canvas()


@app.command("weekly")
def weekly_planner() -> None:
    """Run the weekly planner workflow and print a summary."""
    controller = AgentController()
    summary = controller.weekly_planner()
    console.print(Panel(summary, title="Weekly Planner"))


@app.command("daily")
def daily_briefing() -> None:
    """Run the daily briefing workflow and print a summary."""
    controller = AgentController()
    summary = controller.daily_briefing()
    console.print(Panel(summary, title="Daily Briefing"))
