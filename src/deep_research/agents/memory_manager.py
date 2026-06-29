from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient

from ..config import LLM_CONFIG
from ..memory import ResearchMemoryStore


def create_memory_manager(model_client=None):
    if model_client is None:
        model_client = OllamaChatCompletionClient(
            model=LLM_CONFIG["model_2"],
            host=LLM_CONFIG["base_url"],
            model_info=ModelInfo(
                vision=False,
                function_calling=True,
                json_output=True,
                structured_output=True,
                family="unknown",
            ),
        )
    return AssistantAgent(
        name="ResearchMemory",
        model_client=model_client,
        tools=[],
        system_message=(
            "You are the research memory manager. "
            "Your responsibilities:\n"
            "1. Store research findings in persistent memory for later retrieval\n"
            "2. Retrieve findings by topic to support ongoing research\n"
            "3. List all stored findings on request\n"
            "4. Maintain a structured knowledge base of all discovered information"
        ),
    )
