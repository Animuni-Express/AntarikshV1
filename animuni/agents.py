import httpx
import json
from typing import List, Dict, Any, Optional
from .config import AgentConfig

class AgentInterface:
    def __init__(self, config: AgentConfig):
        self.config = config

    async def chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if self.config.provider == "Local/Ollama":
            return await self._chat_ollama(prompt, system_prompt)
        elif self.config.provider == "Remote/OpenRouter":
            return await self._chat_openrouter(prompt, system_prompt)
        else:
            raise ValueError(f"Unknown provider: {self.config.provider}")

    async def _chat_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        payload = {
            "model": self.config.model,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "stream": False
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.config.endpoint, json=payload, timeout=60.0)
                response.raise_for_status()
                return response.json().get("response", "")
            except Exception as e:
                return f"Error contacting Ollama: {str(e)}"

    async def _chat_openrouter(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
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
            try:
                response = await client.post(self.config.endpoint, json=payload, headers=headers, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                return f"Error contacting OpenRouter: {str(e)}"
