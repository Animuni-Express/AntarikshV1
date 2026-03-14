import typer
import asyncio
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from .config import AgentConfig, save_config, load_config
from .utils import check_resources, get_local_agent_count
from .orchestrator import Orchestrator
from .agents import AgentInterface

__version__ = "0.1.0"

app = typer.Typer(
    add_completion=False,
)
console = Console()

# Technical Mono theme: emerald-green on black background
THEME_STYLE = "bold spring_green3"

ASCII_ART = """
   ▄████████  ███▄▄▄▄      ▄█  ███▄▄▄▄    ███    █▄  ███▄▄▄▄   ▄█
  ███    ███  ███▀▀▀██▄   ███  ███▀▀▀██▄  ███    ███ ███▀▀▀██▄ ███
  ███    ███  ███   ███   ███▌ ███   ███  ███    ███ ███   ███ ███▌
  ███    ███  ███   ███   ███▌ ███   ███  ███    ███ ███   ███ ███▌
▀███████████  ███   ███   ███▌ ███   ███  ███    ███ ███   ███ ███▌
  ███    ███  ███   ███   ███  ███   ███  ███    ███ ███   ███ ███
  ███    ███  ███   ███   ███  ███   ███  ███    ███ ███   ███ ███
  ███    █▀    ▀█   █▀    █▀    ▀█   █▀   ████████▀   ▀█   █▀  █▀

         A N I M U N I   E X P R E S S   O R C H E S T R A T O R
"""

def version_callback(value: bool):
    if value:
        console.print(f"Animuni Express version: {__version__}")
        raise typer.Exit()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Show version and exit."
    ),
):
    """
    Animuni Express: A professional multi-agent orchestrator for resource-constrained systems.
    """
    if ctx.invoked_subcommand is None:
        console.print(Text(ASCII_ART, style=THEME_STYLE))
        console.print(ctx.get_help())

@app.command()
def setup():
    """
    Wizard to configure agents for Animuni Express.
    """
    console.print(Text(ASCII_ART, style=THEME_STYLE))
    console.print(Panel("[bold]Agent Setup Wizard[/bold]", style=THEME_STYLE, border_style=THEME_STYLE))

    agents = load_config()

    while True:
        name = Prompt.ask("Agent Name", console=console)
        provider = Prompt.ask("Provider", choices=["Local/Ollama", "Remote/OpenRouter"], default="Local/Ollama", console=console)
        endpoint = Prompt.ask("API Endpoint", default="http://localhost:11434/api/generate" if provider == "Local/Ollama" else "https://openrouter.ai/api/v1/chat/completions", console=console)
        model = Prompt.ask("Model Name", default="llama3" if provider == "Local/Ollama" else "openai/gpt-3.5-turbo", console=console)

        api_key = None
        if provider == "Remote/OpenRouter":
            api_key = Prompt.ask("API Key", password=True, console=console)

        is_primary = Confirm.ask("Set as Primary Agent?", default=len(agents) == 0, console=console)

        # If this is set as primary, unset others
        if is_primary:
            for a in agents:
                a.is_primary = False

        agents.append(AgentConfig(
            name=name,
            provider=provider,
            endpoint=endpoint,
            model=model,
            api_key=api_key,
            is_primary=is_primary
        ))

        if not Confirm.ask("Add another agent?", default=False, console=console):
            break

    save_config(agents)
    console.print(f"[{THEME_STYLE}]Configuration saved.[/{THEME_STYLE}]")

@app.command()
def list_agents():
    """
    List all configured agents.
    """
    agents = load_config()
    if not agents:
        console.print("[yellow]No agents configured.[/yellow]")
        return

    table = Table(title="Configured Agents", show_header=True, header_style=THEME_STYLE, border_style=THEME_STYLE)
    table.add_column("Name", style="cyan")
    table.add_column("Provider", style="white")
    table.add_column("Model", style="white")
    table.add_column("Primary", style="bold green")

    for a in agents:
        table.add_row(
            a.name,
            a.provider,
            a.model,
            "✔" if a.is_primary else "✘"
        )

    console.print(table)

@app.command()
def remove(name: str):
    """
    Remove an agent by name.
    """
    agents = load_config()
    new_agents = [a for a in agents if a.name != name]

    if len(agents) == len(new_agents):
        console.print(f"[red]Agent '{name}' not found.[/red]")
        return

    save_config(new_agents)
    console.print(f"[{THEME_STYLE}]Agent '{name}' removed.[/{THEME_STYLE}]")

@app.command()
def run(
    task: str,
    primary: str = typer.Option(None, "--primary", "-p", help="Name of the agent to use as primary"),
    model: str = typer.Option(None, "--model", "-m", help="Override the model for this run"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable speed hack (response caching)")
):
    """
    Run a task using the configured agent swarm.
    """
    agents = load_config()
    if not agents:
        console.print("[bold red]No agents configured. Run 'animuni setup' first.[/bold red]")
        return

    # Resource Guard
    local_count = get_local_agent_count(agents)
    check_resources(local_count)

    console.print(Panel(f"Task: [bold white]{task}[/bold white]", title="[bold]Antariksh Swarm Execution[/bold]", border_style=THEME_STYLE, style=THEME_STYLE))

    if primary:
        found = False
        for a in agents:
            if a.name == primary:
                a.is_primary = True
                found = True
            else:
                a.is_primary = False
        if not found:
            console.print(f"[bold red]Primary agent '{primary}' not found.[/bold red]")
            return

    if model:
        for a in agents:
            a.model = model

    orchestrator = Orchestrator(agents, use_cache=not no_cache)
    asyncio.run(orchestrator.run_task(task))

@app.command()
def test():
    """
    Test connectivity and status of all configured agents.
    """
    agents = load_config()
    if not agents:
        console.print("[bold red]No agents configured.[/bold red]")
        return

    async def test_all():
        table = Table(title="Agent Connectivity Test", show_header=True, header_style=THEME_STYLE, border_style=THEME_STYLE)
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Latency", style="magenta")

        import time
        for agent_cfg in agents:
            interface = AgentInterface(agent_cfg)
            start_time = time.time()
            try:
                response = await interface.chat("Hello, response 'ok' if you hear me.")
                duration = time.time() - start_time
                if "Error" in response:
                    table.add_row(agent_cfg.name, "[red]Offline[/red]", f"{duration:.2f}s")
                else:
                    table.add_row(agent_cfg.name, "[green]Online[/green]", f"{duration:.2f}s")
            except Exception as e:
                table.add_row(agent_cfg.name, f"[red]Error[/red]", "N/A")

        console.print(table)

    asyncio.run(test_all())

@app.command()
def chat(
    agent_name: str = typer.Option(None, "--agent", "-a", help="Name of the agent to chat with")
):
    """
    Direct interactive chat with an agent for prompt testing.
    """
    agents = load_config()
    if not agents:
        console.print("[bold red]No agents configured.[/bold red]")
        return

    if agent_name:
        agent_cfg = next((a for a in agents if a.name == agent_name), None)
        if not agent_cfg:
            console.print(f"[bold red]Agent '{agent_name}' not found.[/bold red]")
            return
    else:
        # Default to primary
        agent_cfg = next((a for a in agents if a.is_primary), agents[0])

    console.print(Panel(f"Session: [bold]{agent_cfg.name}[/bold] | Model: [italic]{agent_cfg.model}[/italic]", border_style=THEME_STYLE, style=THEME_STYLE))

    interface = AgentInterface(agent_cfg)

    async def chat_loop():
        while True:
            user_input = Prompt.ask(f"[{THEME_STYLE}]User[/{THEME_STYLE}]", console=console)
            if user_input.lower() in ["exit", "quit"]:
                break

            with console.status(f"[{THEME_STYLE}]Swarm processing...[/{THEME_STYLE}]"):
                response = await interface.chat(user_input)

            console.print(Panel(response, title=f"[{THEME_STYLE}]{agent_cfg.name}[/{THEME_STYLE}]", border_style=THEME_STYLE))

    asyncio.run(chat_loop())

if __name__ == "__main__":
    app()
