from __future__ import annotations

import re
from io import BytesIO

from pypdf import PdfReader


class DocumentProcessingService:
    def process_pdf(self, filename: str, file_bytes: bytes) -> dict[str, str]:
        text = self.extract_text_from_pdf(file_bytes)
        cleaned_text = self._clean_text(text)
        return {
            "filename": filename,
            "text": cleaned_text,
            "title": self._infer_title(cleaned_text),
            "abstract": self._extract_section(cleaned_text, ["abstract"], ["introduction", "keywords", "1 introduction"]),
            "conclusion": self._extract_section(
                cleaned_text,
                ["conclusion", "conclusions"],
                ["references", "acknowledgments", "acknowledgements", "future work"],
            ),
        }

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(file_bytes))
        parts: list[str] = []
        for page in reader.pages:
            extracted = page.extract_text() or ""
            if extracted.strip():
                parts.append(extracted)
        return "\n".join(parts).strip()

    def _infer_title(self, text: str) -> str:
        for line in text.splitlines():
            candidate = line.strip()
            if 10 <= len(candidate) <= 180 and not self._looks_like_heading(candidate):
                return candidate
        return "Untitled uploaded paper"

    def _extract_section(self, text: str, start_markers: list[str], end_markers: list[str]) -> str:
        lines = [line.strip() for line in text.splitlines()]
        start_index = None
        for index, line in enumerate(lines):
            normalized = self._normalize_heading(line)
            if normalized in start_markers:
                start_index = index + 1
                break

        if start_index is None:
            return ""

        collected: list[str] = []
        for line in lines[start_index:]:
            normalized = self._normalize_heading(line)
            if normalized in end_markers:
                break
            if line:
                collected.append(line)
        return " ".join(collected).strip()

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"\r\n?", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _normalize_heading(value: str) -> str:
        return re.sub(r"[^a-z0-9 ]+", "", value.lower()).strip()

    @staticmethod
    def _looks_like_heading(value: str) -> bool:
        normalized = re.sub(r"[^a-z0-9 ]+", "", value.lower()).strip()
        return normalized in {
            "abstract",
            "introduction",
            "keywords",
            "conclusion",
            "conclusions",
            "references",
        }
