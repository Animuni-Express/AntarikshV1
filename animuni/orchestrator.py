import asyncio
from typing import List, Dict, Any
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from .config import AgentConfig
from .agents import AgentInterface

console = Console()
THEME_STYLE = "bold spring_green3"

class Orchestrator:
    def __init__(self, agents: List[AgentConfig]):
        self.agents = agents
        self.primary = next((a for a in agents if a.is_primary), agents[0] if agents else None)
        self.secondaries = [a for a in agents if a != self.primary]

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
            p_task = progress.add_task(description=f"Primary Agent ({self.primary.name}) is planning...", total=None)
            primary_interface = AgentInterface(self.primary)

            system_prompt = (
                "You are the Primary Orchestrator. Break down the user's task into sub-tasks "
                "that can be handled by secondary agents. Output the plan clearly."
            )
            plan = await primary_interface.chat(task, system_prompt=system_prompt)
            progress.update(p_task, completed=True, description="Planning complete.")

            console.print(Panel(plan, title="Chain of Thought Plan", border_style=THEME_STYLE))

            # Step 2: Sub-task distribution
            # For simplicity, we'll ask secondary agents to execute based on the plan.
            # In a more complex setup, we'd parse the plan and distribute.

            results = []

            async def run_secondary(agent_config, sub_task):
                s_task = progress.add_task(description=f"Agent {agent_config.name} executing...", total=None)
                interface = AgentInterface(agent_config)
                res = await interface.chat(f"Based on this plan:\n{plan}\n\nExecute your part for: {sub_task}")
                progress.update(s_task, completed=True, description=f"Agent {agent_config.name} finished.")
                return agent_config.name, res

            if self.secondaries:
                tasks = []
                for i, agent in enumerate(self.secondaries):
                    # Distribute work (naive split for this demo)
                    tasks.append(run_secondary(agent, task))

                results = await asyncio.gather(*tasks)

            # Final Summary
            table = Table(title="Antariksh Swarm Execution Results", show_header=True, header_style=THEME_STYLE)
            table.add_column("Agent", style="cyan")
            table.add_column("Result", style="white")

            for agent_name, result in results:
                table.add_row(agent_name, result[:200] + "..." if len(result) > 200 else result)

            console.print(table)

            # Final touch: consolidated response from primary
            summary_task = progress.add_task(description="Consolidating final result...", total=None)
            final_prompt = f"Based on the following execution results from the swarm, provide a final response to the user's task: {task}\n\nResults:\n" + \
                           "\n".join([f"{n}: {r}" for n, r in results])

            final_response = await primary_interface.chat(final_prompt)
            progress.update(summary_task, completed=True)

            console.print(Panel(final_response, title="Final Swarm Response", border_style=THEME_STYLE, style=THEME_STYLE))
