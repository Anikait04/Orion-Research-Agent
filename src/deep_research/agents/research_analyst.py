from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import ModelInfo

from ..tools.verify_source import verify_source_tool
from ..config import LLM_CONFIG

def create_research_analyst(model_client=None):
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
        name="ResearchAnalyst",
        model_client=model_client,
        tools=[verify_source_tool],
        system_message=(
            "You are a research analyst. Your role is to cross-reference claims across multiple sources, "
            "assign confidence scores based on source quality and consensus, "
            "flag contradictions when sources disagree, "
            "assess overall credibility of findings, "
            "and provide structured analysis output. "
            "Use the verify_source_tool to validate claims against collected sources."
        ),
    )
