from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient

from ..config import LLM_CONFIG
from ..tools import web_search_tool, arxiv_search_tool, crawl_links_tool


def create_search_specialist(model_client=None):
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
        name="SearchSpecialist",
        model_client=model_client,
        tools=[web_search_tool, arxiv_search_tool, crawl_links_tool],
        system_message=(
            "You are a search specialist agent responsible for gathering information. "
            "Your responsibilities:\n"
            "1. Formulate effective search queries tailored to the research topic\n"
            "2. Use multiple search engines (web, academic) to maximize coverage\n"
            "3. Triage results by relevance, discarding irrelevant ones\n"
            "4. Crawl promising seed URLs when needed for deeper exploration\n"
            "5. Return structured results for the next agent"
        ),
    )
