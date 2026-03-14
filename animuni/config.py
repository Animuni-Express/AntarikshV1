import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, ValidationError

CONFIG_FILE = Path("agents.json")

class AgentConfig(BaseModel):
    name: str
    provider: str  # "Local/Ollama" or "Remote/OpenRouter"
    endpoint: str
    model: str = "llama3" # Default model
    api_key: Optional[str] = None
    is_primary: bool = False

def load_config() -> List[AgentConfig]:
    if not CONFIG_FILE.exists():
        return []
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return [AgentConfig(**agent) for agent in data]
    except (json.JSONDecodeError, ValidationError):
        return []

def save_config(agents: List[AgentConfig]):
    with open(CONFIG_FILE, "w") as f:
        json.dump([agent.model_dump() for agent in agents], f, indent=4)
