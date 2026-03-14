import psutil
from rich.console import Console

console = Console()

def check_resources(num_local_agents: int):
    """
    Checks if the system has enough memory to run the requested number of local agents.
    8GB is the reference for this system.
    """
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    available_gb = mem.available / (1024**3)

    # Heuristic: Each local agent might need ~2-4GB depending on the model.
    # If total RAM is low (<= 8GB), warn if more than 1 local agent is running.
    if total_gb <= 8.5 and num_local_agents > 1:
        console.print(f"[bold yellow]Warning:[/bold yellow] You have {total_gb:.1f}GB total RAM. "
                      f"Running {num_local_agents} local agents might exceed your system resources.")

    if available_gb < 1.0:
        console.print(f"[bold red]Critical:[/bold red] Only {available_gb:.1f}GB RAM available. "
                      "Performance might be severely impacted.")

def get_local_agent_count(agents) -> int:
    return sum(1 for a in agents if a.provider == "Local/Ollama")
