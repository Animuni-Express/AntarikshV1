# Animuni Express CLI

Animuni Express is a professional Python-based multi-agent orchestrator designed for resource-constrained systems (e.g., 8GB RAM with iGPU). It allows you to coordinate multiple AI agents (Local via Ollama or Remote via OpenRouter) to solve complex tasks using a "Chain of Thought" orchestration pattern.

## Features

- **Technical Mono UI**: Emerald-green on black terminal aesthetic using `Rich`.
- **Dynamic Swarm**: Easily configure and manage multiple local and remote agents.
- **CoT Orchestration**: Automatically breaks down tasks into sub-tasks for a swarm of agents.
- **Resource Guard**: Built-in memory monitoring to prevent system overload on local hardware.
- **Iterative Testing**: `test` and `chat` commands for rapid model and prompt evaluation.

## Installation

```bash
pip install .
```

## Quick Start

1. **Setup Agents**:
   ```bash
   animuni setup
   ```
   Follow the wizard to add at least one Primary agent.

2. **Verify Connectivity**:
   ```bash
   animuni test
   ```

3. **Run a Task**:
   ```bash
   animuni run "Research the latest trends in autonomous agent frameworks and summarize them."
   ```

## CLI Reference

- `setup`: Interactive configuration wizard.
- `run`: Execute a task with the agent swarm.
  - `-p, --primary`: Override the primary agent for the run.
  - `-m, --model`: Override the model for the run.
- `list-agents`: Show all configured agents.
- `remove`: Delete an agent configuration.
- `test`: Connectivity check for all agents.
- `chat`: Direct interactive session with an agent.
- `--version`: Show current version.

## Architecture

Animuni Express utilizes a **Primary-Secondary** architecture:
1. **Primary Agent**: Receives the initial task and generates a decomposition plan (Chain of Thought).
2. **Secondary Agents**: Receive specific sub-tasks based on the plan and execute them.
3. **Consolidation**: The Primary agent gathers results and provides a final synthesised response.

## License

MIT
