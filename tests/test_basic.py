import unittest
from animuni.config import AgentConfig, save_config, load_config
from animuni.utils import get_local_agent_count
import os

class TestAnimuni(unittest.TestCase):
    def test_config_save_load(self):
        test_agents = [
            AgentConfig(name="Test1", provider="Local/Ollama", endpoint="http://test", is_primary=True),
            AgentConfig(name="Test2", provider="Remote/OpenRouter", endpoint="http://test2", api_key="abc")
        ]
        save_config(test_agents)
        loaded_agents = load_config()
        self.assertEqual(len(loaded_agents), 2)
        self.assertEqual(loaded_agents[0].name, "Test1")
        self.assertTrue(loaded_agents[0].is_primary)
        self.assertEqual(loaded_agents[1].api_key, "abc")

    def test_local_agent_count(self):
        agents = [
            AgentConfig(name="L1", provider="Local/Ollama", endpoint="x"),
            AgentConfig(name="R1", provider="Remote/OpenRouter", endpoint="y"),
            AgentConfig(name="L2", provider="Local/Ollama", endpoint="z")
        ]
        self.assertEqual(get_local_agent_count(agents), 2)

if __name__ == "__main__":
    unittest.main()
