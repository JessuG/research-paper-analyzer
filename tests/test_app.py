from sqlalchemy.orm import Session

from app import main
from app.models import PaperSubmission


def test_index_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Research Paper Analyser" in response.text
    assert "Submit a Paper" in response.text
    assert "Upload a PDF" in response.text


def test_submit_paper_saves_analysis_and_redirects(client, session: Session, monkeypatch):
    fake_analysis = {
        "methodology": "- Evaluated a benchmark dataset\n- Compared baseline systems",
        "findings": "- Improved classification accuracy\n- Identified stronger performance",
        "research_gaps": "- Cross-domain testing is limited\n- More diverse datasets are needed",
    }

    def fake_analyze(self, title: str, abstract: str, conclusion: str):
        return fake_analysis

    monkeypatch.setattr(main.PaperAnalysisService, "analyze", fake_analyze)

    response = client.post(
        "/submit",
        data={
            "title": "Benchmarking Transformer Models for Text Classification",
            "abstract": (
                "This paper evaluates a transformer-based text classification pipeline using benchmark "
                "datasets, baseline comparisons, and error analysis across multiple tasks."
            ),
            "conclusion": (
                "The proposed setup improves accuracy over baselines, but broader domain transfer "
                "and robustness remain open for future study."
            ),
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    saved = session.query(PaperSubmission).one()
    assert saved.title == "Benchmarking Transformer Models for Text Classification"
    assert saved.methodology == fake_analysis["methodology"]
    assert saved.findings == fake_analysis["findings"]
    assert saved.research_gaps == fake_analysis["research_gaps"]


def test_saved_submission_is_rendered_on_homepage(client, session: Session):
    submission = PaperSubmission(
        title="Existing Review Sample",
        abstract="An abstract that is long enough to be realistic for rendering in the app.",
        conclusion="A conclusion that is also long enough to appear in the review list.",
        methodology="- Surveyed prior work",
        findings="- Found a measurable improvement",
        research_gaps="- Needs larger-scale validation",
    )
    session.add(submission)
    session.commit()

    response = client.get("/")

    assert response.status_code == 200
    assert "Existing Review Sample" in response.text
    assert "Found a measurable improvement" in response.text
    assert "Needs larger-scale validation" in response.text


def test_upload_prefills_form_after_classification(client, monkeypatch):
    fake_processed = {
        "filename": "sample.pdf",
        "text": "Abstract Introduction Methods Results Conclusion References",
        "title": "Uploaded Paper Title",
        "abstract": "Uploaded abstract content that is long enough to be useful.",
        "conclusion": "Uploaded conclusion content that is long enough to be useful.",
    }
    fake_review = {
        "is_research_article": True,
        "label": "Research article",
        "confidence": "high",
        "reason": "The document includes standard academic sections.",
    }

    def fake_process_pdf(self, filename: str, file_bytes: bytes):
        return fake_processed

    def fake_classify(self, document_text: str):
        return fake_review

    monkeypatch.setattr(main.DocumentProcessingService, "process_pdf", fake_process_pdf)
    monkeypatch.setattr(main.DocumentClassificationService, "classify", fake_classify)

    response = client.post(
        "/upload",
        files={"paper_file": ("sample.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )

    assert response.status_code == 200
    assert "Upload Review" in response.text
    assert "Research article" in response.text
    assert "Uploaded Paper Title" in response.text
    assert "Uploaded abstract content that is long enough to be useful." in response.text
