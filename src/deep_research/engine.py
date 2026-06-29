from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.base import TaskResult
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import ModelInfo
from .logs import logger
from .config import LLM_CONFIG, RESEARCH_DEFAULTS
from .models import ResearchQuery, ResearchPlan, Finding, Citation, ResearchReport, ProgressLedger
from .agents import (
    create_search_specialist,
    create_deep_extractor,
    create_research_analyst,
    create_report_synthesizer,
    create_orchestrator,
    create_memory_manager,
)
from .memory import ResearchMemoryStore, ResearchSession, save_session


class ResearchEngine:
    logger.info("Inside ResearchEngine")
    def __init__(self, depth: int | None = None):
        self._depth = depth or RESEARCH_DEFAULTS["depth"]
        self._max_iterations = RESEARCH_DEFAULTS["max_iterations"]
        self._model_client = OllamaChatCompletionClient(
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
        self.memory = ResearchMemoryStore()

    def _create_team(self, query: str) -> SelectorGroupChat:
        logger.info("Teams created...")
        search_specialist = create_search_specialist(self._model_client)
        deep_extractor = create_deep_extractor(self._model_client)
        research_analyst = create_research_analyst(self._model_client)
        report_synthesizer = create_report_synthesizer(self._model_client)
        memory_manager = create_memory_manager(self._model_client)
        orchestrator = create_orchestrator(self._model_client)

        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=20)

        return SelectorGroupChat(
            participants=[
                search_specialist,
                deep_extractor,
                research_analyst,
                report_synthesizer,
                orchestrator,
                memory_manager,
            ],
            model_client=self._model_client,
            termination_condition=termination,
            max_turns=self._max_iterations,
        )

    async def run(self, query: str, output_format: str = "markdown") -> ResearchReport:
        logger.info("Inside agents run")
        research_query = ResearchQuery(query=query, depth=self._depth, output_format=output_format)
        team = self._create_team(query)
        try:
            logger.info("gathering data ")
            result: TaskResult = await team.run(task=query)
            logger.info("gathering data done")
            report_text = self._extract_report(result.messages)
            logger.info("generated report")
        except Exception as e:
            return ResearchReport(
                query=research_query,
                conclusion=f"Research failed with error: {e}",
            )

        report = ResearchReport(
            query=research_query,
            executive_summary=report_text,
        )
        logger.info("report done")

        session = ResearchSession(
            query=query,
            depth=self._depth,
            output_format=output_format,
            status="completed",
        )
        save_session(session)
        logger.info("session saved")
        return report

    @staticmethod
    def _extract_report(messages: list) -> str:
        for message in reversed(messages):
            if getattr(message, "source", None) == "ReportSynthesizer":
                content = message.content
                if isinstance(content, list):
                    text = " ".join(
                        item.text for item in content if hasattr(item, "text")
                    )
                else:
                    text = str(content)
                if text.endswith("TERMINATE"):
                    text = text[:-9].rstrip()
                return text
        return ""


__all__ = ["ResearchEngine"]
