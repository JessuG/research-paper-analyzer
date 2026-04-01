from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from crewai import Task


def build_methodology_task(agent, summary_file: Path):
    return Task(
        description=dedent(
            f"""
            Read the paper summary from the file at `{summary_file}` using your available tools.
            Extract the methodology used in the paper.
            Focus on approach, dataset or sample, experiments, and evaluation strategy if present.
            Return 3-5 bullet points.
            """
        ).strip(),
        expected_output="A short bullet list describing the methodology used in the paper.",
        agent=agent,
    )


def build_findings_task(agent, summary_file: Path):
    return Task(
        description=dedent(
            f"""
            Read the paper summary from the file at `{summary_file}` using your available tools.
            Identify the key findings and contributions.
            Return 3-5 bullet points with clear, non-hyped language.
            """
        ).strip(),
        expected_output="A short bullet list of the paper's main findings and contributions.",
        agent=agent,
    )


def build_gaps_task(agent, summary_file: Path):
    return Task(
        description=dedent(
            f"""
            Read the paper summary from the file at `{summary_file}` using your available tools.
            Identify explicit or implied research gaps.
            Consider limitations, unexplored areas, and future directions.
            Return 3-5 bullet points.
            """
        ).strip(),
        expected_output="A short bullet list of research gaps or future work opportunities.",
        agent=agent,
    )
