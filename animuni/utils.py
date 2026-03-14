import ctypes
import os
from pathlib import Path
from rich.console import Console

console = Console()

# Load C++ shared library
lib_path = Path(__file__).parent / "libmonitor.so"
try:
    lib = ctypes.CDLL(str(lib_path))
    lib.get_memory_usage.restype = ctypes.c_float
    lib.get_total_memory.restype = ctypes.c_float
    HAS_CPP_MONITOR = True
except Exception:
    HAS_CPP_MONITOR = False

def check_resources(num_local_agents: int):
    """
    Checks if the system has enough memory to run the requested number of local agents.
    Uses C++ monitor if available, else falls back to psutil logic (simplified here).
    """
    if HAS_CPP_MONITOR:
        total_gb = lib.get_total_memory()
        available_gb = lib.get_memory_usage()
    else:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        available_gb = mem.available / (1024**3)

    if total_gb <= 8.5 and num_local_agents > 1:
        console.print(f"[bold yellow]Hardware Warning:[/bold yellow] {total_gb:.1f}GB total RAM detected. "
                      f"Running {num_local_agents} local agents may cause swapping.")

    if available_gb < 1.0:
        console.print(f"[bold red]Critical Resource Alert:[/bold red] Only {available_gb:.1f}GB RAM available.")

def get_local_agent_count(agents) -> int:
    return sum(1 for a in agents if a.provider == "Local/Ollama")
