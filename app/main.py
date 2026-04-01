from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.analysis import DocumentClassificationService, PaperAnalysisService
from app.config import settings
from app.database import Base, engine, get_db
from app.document_processing import DocumentProcessingService
from app.models import PaperSubmission
from app.schemas import PaperSubmissionCreate

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


def render_index(
    request: Request,
    db: Session,
    *,
    form_data: dict[str, str] | None = None,
    upload_review: dict | None = None,
    upload_error: str = "",
):
    submissions = db.query(PaperSubmission).order_by(PaperSubmission.created_at.desc(), PaperSubmission.id.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "submissions": submissions,
            "app_name": settings.app_name,
            "form_data": form_data or {"title": "", "abstract": "", "conclusion": ""},
            "upload_review": upload_review,
            "upload_error": upload_error,
        },
    )


@app.get("/")
def read_index(request: Request, db: Session = Depends(get_db)):
    return render_index(request, db)


@app.post("/upload")
async def upload_paper(
    request: Request,
    paper_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not paper_file.filename or not paper_file.filename.lower().endswith(".pdf"):
        return render_index(request, db, upload_error="Please upload a PDF research paper.")

    file_bytes = await paper_file.read()
    if not file_bytes:
        return render_index(request, db, upload_error="The uploaded file was empty.")

    processor = DocumentProcessingService()
    processed = processor.process_pdf(paper_file.filename, file_bytes)

    if not processed["text"]:
        return render_index(
            request,
            db,
            upload_error="No readable text could be extracted from that PDF. Try a text-based PDF instead.",
        )

    classifier = DocumentClassificationService()
    upload_review = classifier.classify(processed["text"])
    upload_review["filename"] = processed["filename"]

    return render_index(
        request,
        db,
        form_data={
            "title": processed["title"],
            "abstract": processed["abstract"],
            "conclusion": processed["conclusion"],
        },
        upload_review=upload_review,
    )


@app.post("/submit")
def submit_paper(
    title: str = Form(...),
    abstract: str = Form(...),
    conclusion: str = Form(...),
    db: Session = Depends(get_db),
):
    form_data = PaperSubmissionCreate(title=title, abstract=abstract, conclusion=conclusion)
    analysis_service = PaperAnalysisService()
    analysis = analysis_service.analyze(
        title=form_data.title,
        abstract=form_data.abstract,
        conclusion=form_data.conclusion,
    )

    submission = PaperSubmission(
        title=form_data.title,
        abstract=form_data.abstract,
        conclusion=form_data.conclusion,
        methodology=analysis["methodology"],
        findings=analysis["findings"],
        research_gaps=analysis["research_gaps"],
    )
    db.add(submission)
    db.commit()

    return RedirectResponse(url="/", status_code=303)
