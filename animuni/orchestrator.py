import asyncio
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from .config import AgentConfig
from .agents import AgentInterface

console = Console()
THEME_STYLE = "bold spring_green3"
CACHE_DIR = Path(".animuni_cache")

def get_cache_path(prompt: str, agent_name: str) -> Path:
    """
    Generate a deterministic cache file path for a given prompt and agent.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    key = f"{agent_name}:{prompt}".encode()
    fname = hashlib.sha256(key).hexdigest()
    return CACHE_DIR / f"{fname}.txt"

class Orchestrator:
    def __init__(self, agents: List[AgentConfig], use_cache: bool = True):
        self.agents = agents
        self.primary = next((a for a in agents if a.is_primary), agents[0] if agents else None)
        self.secondaries = [a for a in agents if a != self.primary]
        self.use_cache = use_cache

    async def _get_response(self, interface: AgentInterface, prompt: str, system_prompt: str = None) -> str:
        if self.use_cache:
            cp = get_cache_path(prompt, interface.config.name)
            if cp.exists():
                return cp.read_text()

        res = await interface.chat(prompt, system_prompt=system_prompt)

        if self.use_cache and "Error" not in res:
            cp = get_cache_path(prompt, interface.config.name)
            cp.write_text(res)
        return res

    async def run_task(self, task: str):
        if not self.primary:
            console.print("[bold red]Error: No primary agent configured.[/bold red]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:

            # Step 1: Planning
            p_task = progress.add_task(description=f"Primary ({self.primary.name}) planning...", total=None)
            primary_interface = AgentInterface(self.primary)

            system_prompt = (
                "You are the Primary Orchestrator. Break down the user's task into sub-tasks. "
                "Output ONLY a JSON list of sub-task strings. Example: [\"task1\", \"task2\"]"
            )
            plan_raw = await self._get_response(primary_interface, task, system_prompt=system_prompt)
            progress.update(p_task, completed=True, description="Planning complete.")

            try:
                import json
                sub_tasks = json.loads(plan_raw)
                if not isinstance(sub_tasks, list): sub_tasks = [task]
            except:
                sub_tasks = [task] # Fallback

            console.print(Panel(f"Swarm Plan: {', '.join(sub_tasks)}", title="Chain of Thought", border_style=THEME_STYLE))

            # Step 2: Parallel execution (Speed Hack)
            results = []
            if self.secondaries and sub_tasks:
                async def run_secondary(agent_cfg, st):
                    s_task = progress.add_task(description=f"Agent {agent_cfg.name} executing {st[:20]}...", total=None)
                    interface = AgentInterface(agent_cfg)
                    res = await self._get_response(interface, st)
                    progress.update(s_task, completed=True, description=f"Agent {agent_cfg.name} done.")
                    return agent_cfg.name, res

                # Distribute tasks among secondaries
                execution_tasks = []
                for i, st in enumerate(sub_tasks):
                    agent = self.secondaries[i % len(self.secondaries)]
                    execution_tasks.append(run_secondary(agent, st))

                results = await asyncio.gather(*execution_tasks)

            # Final Summary Table
            table = Table(title="Execution Results", show_header=True, header_style=THEME_STYLE, border_style=THEME_STYLE)
            table.add_column("Agent", style="cyan")
            table.add_column("Output Preview", style="white")
            for agent_name, result in results:
                table.add_row(agent_name, result[:100] + "...")
            console.print(table)

            # Final Consolidation
            summary_task = progress.add_task(description="Synthesizing final response...", total=None)
            final_prompt = f"Based on these swarm results, give a final answer for: {task}\n\nResults:\n" + \
                           "\n".join([f"{n}: {r}" for n, r in results])

            final_response = await self._get_response(primary_interface, final_prompt)
            progress.update(summary_task, completed=True)

            console.print(Panel(final_response, title="Final Response", border_style=THEME_STYLE, style=THEME_STYLE))
