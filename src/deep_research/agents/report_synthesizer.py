from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import ModelInfo

from ..tools.citations import format_citations_tool
from ..config import LLM_CONFIG


def create_report_synthesizer(model_client=None):
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
        name="ReportSynthesizer",
        model_client=model_client,
        tools=[format_citations_tool],
        system_message=(
            "You are a report synthesizer. Your role is to synthesize all findings into a coherent, "
            "well-structured final report. The report must include an executive summary, methodology, "
            "detailed findings, analysis, and conclusion. Format citations properly using the "
            "format_citations_tool. Ensure every factual claim has a supporting citation. "
            "Output the final report in markdown format. End with the word \"TERMINATE\" on its own line "
            "when the report is complete."
        ),
    )
