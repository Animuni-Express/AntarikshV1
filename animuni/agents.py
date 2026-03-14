import httpx
import json
import logging
from typing import List, Dict, Any, Optional
from .config import AgentConfig

# Setup logger
logger = logging.getLogger("animuni")

class AgentError(Exception):
    """Custom exception for agent-related errors."""
    pass

class AgentInterface:
    def __init__(self, config: AgentConfig):
        self.config = config

    async def chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Sends a prompt to the agent and returns the response.
        """
        try:
            if self.config.provider == "Local/Ollama":
                return await self._chat_ollama(prompt, system_prompt)
            elif self.config.provider == "Remote/OpenRouter":
                return await self._chat_openrouter(prompt, system_prompt)
            else:
                raise ValueError(f"Unknown provider: {self.config.provider}")
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to agent {self.config.name}")
            return f"Error: Request timed out for agent {self.config.name}."
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from agent {self.config.name}: {e.response.status_code}")
            return f"Error: Agent returned HTTP {e.response.status_code}."
        except Exception as e:
            logger.exception(f"Unexpected error with agent {self.config.name}")
            return f"Error: An unexpected error occurred: {str(e)}"

    async def _chat_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.endpoint,
                json=payload,
                timeout=httpx.Timeout(60.0, connect=10.0)
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    async def _chat_openrouter(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/animuni/animuni-express", # Professionalism
            "X-Title": "Animuni Express",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.endpoint,
                json=payload,
                headers=headers,
                timeout=httpx.Timeout(60.0, connect=10.0)
            )
            response.raise_for_status()
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                raise AgentError("Invalid response format from OpenRouter")
