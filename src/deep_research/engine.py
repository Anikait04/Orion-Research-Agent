from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.base import TaskResult
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import ModelInfo
from .logs import logger
from .config import LLM_CONFIG, DEPTH_CONFIG
from .models import ResearchQuery, ResearchReport
from .agents import (
    create_search_specialist,
    create_deep_extractor,
    create_research_analyst,
    create_report_synthesizer,
    create_orchestrator,
    create_memory_manager,
)
from .memory import ResearchMemoryStore, ResearchSession, save_session
from .report.generator import ReportGenerator


class ResearchEngine:
    def __init__(self, depth: int = 3):
        self._depth = depth
        depth_cfg = DEPTH_CONFIG[depth]
        self._max_iterations = depth_cfg["max_iterations"]
        self._crawl_depth = depth_cfg["crawl_depth"]
        self._max_pages = depth_cfg["max_pages"]
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
        self.report_generator = ReportGenerator()
        logger.info("ResearchEngine initialized with depth=%d", depth)

    def _create_team(self, query: str) -> SelectorGroupChat:
        logger.info("Creating research team")
        search_specialist = create_search_specialist(self._model_client)
        deep_extractor = create_deep_extractor(self._model_client)
        research_analyst = create_research_analyst(self._model_client)
        report_synthesizer = create_report_synthesizer(self._model_client)
        memory_manager = create_memory_manager(self._model_client)
        orchestrator = create_orchestrator(self._model_client)

        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(
            max_messages=self._max_iterations
        )

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
        logger.info("Starting research run")
        research_query = ResearchQuery(
            query=query, depth=self._depth, output_format=output_format
        )

        existing_findings = await self.memory.search_all(query)
        if existing_findings:
            logger.info("Found %d existing findings in memory", len(existing_findings))

        team = self._create_team(query)
        try:
            logger.info("Gathering data")
            result: TaskResult = await team.run(task=query)
            logger.info("Data gathering complete")
            report_text = self._extract_report(result.messages)
            logger.info("Report extracted")
        except Exception as e:
            return ResearchReport(
                query=research_query,
                conclusion=f"Research failed with error: {e}",
            )

        report = ResearchReport(
            query=research_query,
            executive_summary=report_text,
        )

        for finding in report.findings:
            await self.memory.store_finding(finding)
        logger.info("Stored %d findings in memory", len(report.findings))

        if output_format == "json":
            output = report.model_dump_json(indent=2)
        else:
            output = self.report_generator.generate(report, fmt="markdown")

        saved_path = self.report_generator.save(output)
        logger.info("Report saved to %s", saved_path)

        session = ResearchSession(
            query=query,
            depth=self._depth,
            output_format=output_format,
            status="completed",
        )
        save_session(session)
        logger.info("Session saved")
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
