from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient

from ..config import LLM_CONFIG


def create_orchestrator(model_client=None):
    if model_client is None:
        model_client = OllamaChatCompletionClient(
            model=LLM_CONFIG["model"],
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
        name="ResearchOrchestrator",
        model_client=model_client,
        tools=[],
        system_message=(
            "You are the research orchestrator. Maintain the research plan and progress ledger throughout the session. "
            "Decide which agent should act next based on the current state. "
            "Track which sub-questions are answered and which need deeper investigation. "
            "Revise the research plan when knowledge gaps are detected. "
            "Delegate to SearchSpecialist for searching, DeepExtractor for extraction, "
            "ResearchAnalyst for analysis, ReportSynthesizer for final report. "
            "Monitor research depth and ensure thorough coverage. "
            "Signal completion when all sub-questions are adequately addressed."
        ),
    )
