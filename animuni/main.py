import typer
import asyncio
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from .config import AgentConfig, save_config, load_config
from .utils import check_resources, get_local_agent_count
from .orchestrator import Orchestrator

app = typer.Typer()
console = Console()

# Technical Mono theme: emerald-green on black background
# Note: Rich styles can handle colors, but background is usually terminal controlled.
# We will use "emerald" equivalent which is often "spring_green3" or similar in Rich,
# or just "green" for high compatibility. Let's try "bold spring_green3"
THEME_STYLE = "bold spring_green3"

@app.command()
def setup():
    """
    Wizard to configure agents for Animuni Express.
    """
    console.print(Panel("[bold]Animuni Express - Agent Setup Wizard[/bold]", style=THEME_STYLE))

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
    console.print(f"[{THEME_STYLE}]Configuration saved to agents.json[/{THEME_STYLE}]")

@app.command()
def run(task: str):
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

    console.print(Panel(f"Task: {task}", title="[bold]Antariksh Swarm[/bold]", border_style=THEME_STYLE, style=THEME_STYLE))

    orchestrator = Orchestrator(agents)
    asyncio.run(orchestrator.run_task(task))

if __name__ == "__main__":
    app()
