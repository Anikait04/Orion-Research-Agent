from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient

from ..config import LLM_CONFIG
from ..tools import web_scraper_tool, pdf_extractor_tool


def create_deep_extractor(model_client=None):
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
        name="DeepExtractor",
        model_client=model_client,
        tools=[web_scraper_tool, pdf_extractor_tool],
        system_message=(
            "You are a deep content extraction agent. "
            "Your responsibilities:\n"
            "1. Scrape full content from provided URLs using WebScraper\n"
            "2. Extract PDF content when papers are found\n"
            "3. Identify key facts, quotes, statistics, and claims\n"
            "4. Structure extracted data into clear findings with source attribution\n"
            "5. Filter out irrelevant or low-quality content"
        ),
    )
