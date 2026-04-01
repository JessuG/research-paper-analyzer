from __future__ import annotations

from crewai import Crew
from crewai.llm import LLM

from app.config import settings
from app.crew.agents import (
    build_extractor_agent,
    build_findings_agent,
    build_gap_agent,
    build_research_classifier_agent,
)
from app.crew.tasks import (
    build_findings_task,
    build_gaps_task,
    build_methodology_task,
    build_research_classifier_task,
)
from app.crew.tools import build_paper_workspace, build_text_workspace, get_crewai_tools


def run_paper_analysis_crew(title: str, abstract: str, conclusion: str) -> dict[str, str]:
    workspace = build_paper_workspace(title=title, abstract=abstract, conclusion=conclusion)
    try:
        llm = LLM(model=f"openai/{settings.openai_model}", api_key=settings.openai_api_key, temperature=0.2)
        tools = get_crewai_tools(summary_file=workspace.summary_file, root_path=workspace.root_path)

        extractor_agent = build_extractor_agent(llm=llm, tools=tools)
        findings_agent = build_findings_agent(llm=llm, tools=tools)
        gap_agent = build_gap_agent(llm=llm, tools=tools)

        methodology_task = build_methodology_task(agent=extractor_agent, summary_file=workspace.summary_file)
        findings_task = build_findings_task(agent=findings_agent, summary_file=workspace.summary_file)
        gaps_task = build_gaps_task(agent=gap_agent, summary_file=workspace.summary_file)

        crew = Crew(
            agents=[extractor_agent, findings_agent, gap_agent],
            tasks=[methodology_task, findings_task, gaps_task],
            verbose=False,
        )
        crew.kickoff()

        return {
            "methodology": str(methodology_task.output).strip(),
            "findings": str(findings_task.output).strip(),
            "research_gaps": str(gaps_task.output).strip(),
        }
    finally:
        workspace.cleanup()


def run_research_article_classifier_crew(document_text: str) -> str:
    workspace = build_text_workspace(filename="uploaded_document.txt", content=document_text)
    try:
        llm = LLM(model=f"openai/{settings.openai_model}", api_key=settings.openai_api_key, temperature=0.1)
        tools = get_crewai_tools(summary_file=workspace.summary_file, root_path=workspace.root_path)
        classifier_agent = build_research_classifier_agent(llm=llm, tools=tools)
        classifier_task = build_research_classifier_task(agent=classifier_agent, summary_file=workspace.summary_file)

        crew = Crew(agents=[classifier_agent], tasks=[classifier_task], verbose=False)
        crew.kickoff()
        return str(classifier_task.output).strip()
    finally:
        workspace.cleanup()
