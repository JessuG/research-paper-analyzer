from __future__ import annotations

from crewai import Agent


def build_extractor_agent(llm, tools):
    return Agent(
        role="Methodology Extractor",
        goal="Extract the research methodology and study design from the paper summary.",
        backstory=(
            "You are skilled at recognizing study design, datasets, experiments, and evaluation methods. "
            "Use the available file tools to inspect the provided paper summary before answering."
        ),
        tools=tools,
        llm=llm,
        verbose=False,
    )


def build_findings_agent(llm, tools):
    return Agent(
        role="Findings Analyst",
        goal="Identify the paper's most important findings, results, and contributions.",
        backstory=(
            "You summarize research outcomes clearly and focus on the main supported claims. "
            "Use the available file tools to inspect the provided paper summary before answering."
        ),
        tools=tools,
        llm=llm,
        verbose=False,
    )


def build_gap_agent(llm, tools):
    return Agent(
        role="Research Gap Analyst",
        goal="Identify research gaps, limitations, and future work implied by the paper summary.",
        backstory=(
            "You specialize in spotting unanswered questions, limitations, and opportunities for future studies. "
            "Use the available file tools to inspect the provided paper summary before answering."
        ),
        tools=tools,
        llm=llm,
        verbose=False,
    )
