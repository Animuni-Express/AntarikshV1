import json
import logging
from experts.logic import LogicExpert
from experts.culture import CultureExpert
from experts.reasoning import ReasoningExpert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AntarikshRouter:
    """
    Antariksh V1 Router
    Uses a Hierarchical Orchestration Pattern.
    - Decomposes user input using a lightweight model (e.g., Qwen2.5-1B logic)
    - Assigns sub-tasks to Experts (1B for logic, 14B for culture, R1 for reasoning)
    - Merges the responses into a final output
    """
    
    def __init__(self):
        self.logic_expert = LogicExpert()
        self.culture_expert = CultureExpert()
        self.reasoning_expert = ReasoningExpert()
    
    def decompose_prompt(self, prompt: str) -> list:
        """
        In a real application, this uses Qwen2.5-1B to classify the prompt
        into a JSON structure of sub-tasks.
        """
        logger.info("Decomposing prompt into sub-tasks...")
        # Mock decomposition for testing structure
        return [
            {"task_type": "reasoning", "instruction": f"Analyze: {prompt}"},
            {"task_type": "culture", "instruction": "Provide Indian context to the analysis."},
            {"task_type": "logic", "instruction": "Structure the final response."}
        ]

    def assign_to_experts(self, sub_tasks: list) -> dict:
        """
        Routes the sub-tasks to the appropriatve expert models.
        """
        results = {}
        for idx, task in enumerate(sub_tasks):
            task_type = task.get("task_type")
            instruction = task.get("instruction")
            logger.info(f"Assigning task {idx} to {task_type} expert...")
            
            if task_type == "reasoning":
                results['reasoning'] = self.reasoning_expert.execute(instruction)
            elif task_type == "culture":
                results['culture'] = self.culture_expert.execute(instruction)
            elif task_type == "logic":
                results['logic'] = self.logic_expert.execute(instruction)
            else:
                logger.warning(f"Unknown task type: {task_type}")
        
        return results

    def merge_results(self, results: dict) -> str:
        """
        Merges results from multiple experts into a single output.
        """
        logger.info("Merging expert results...")
        final_output = f"""
Antariksh V1 Synthesis:
---
Reasoning (R1): {results.get('reasoning')}
Culture (14B): {results.get('culture')}
Logic Synthesis (1B): {results.get('logic')}
"""
        return final_output.strip()

    def process(self, user_prompt: str) -> str:
        sub_tasks = self.decompose_prompt(user_prompt)
        expert_results = self.assign_to_experts(sub_tasks)
        final_response = self.merge_results(expert_results)
        return final_response

if __name__ == "__main__":
    router = AntarikshRouter()
    prompt = "Explain quantum computing and its potential impact on rural Indian farmers."
    response = router.process(prompt)
    print("\n" + response)
