from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

try:
    from crewai_tools import DirectoryReadTool, FileReadTool
except ImportError:  # pragma: no cover
    DirectoryReadTool = FileReadTool = None


@dataclass
class PaperWorkspace:
    directory: TemporaryDirectory[str]
    root_path: Path
    summary_file: Path

    def cleanup(self) -> None:
        self.directory.cleanup()


def build_paper_workspace(title: str, abstract: str, conclusion: str) -> PaperWorkspace:
    temp_dir = TemporaryDirectory()
    root_path = Path(temp_dir.name)
    summary_file = root_path / "paper_summary.txt"
    summary_file.write_text(
        "\n\n".join(
            [
                f"Title:\n{title.strip()}",
                f"Abstract:\n{abstract.strip()}",
                f"Conclusion:\n{conclusion.strip()}",
            ]
        ),
        encoding="utf-8",
    )
    return PaperWorkspace(directory=temp_dir, root_path=root_path, summary_file=summary_file)


def get_crewai_tools(summary_file: Path, root_path: Path):
    if not FileReadTool or not DirectoryReadTool:
        return []

    return [
        FileReadTool(file_path=str(summary_file)),
        DirectoryReadTool(directory=str(root_path)),
    ]
