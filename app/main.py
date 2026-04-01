from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.analysis import PaperAnalysisService
from app.config import settings
from app.database import Base, engine, get_db
from app.models import PaperSubmission
from app.schemas import PaperSubmissionCreate

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_index(request: Request, db: Session = Depends(get_db)):
    submissions = db.query(PaperSubmission).order_by(PaperSubmission.created_at.desc(), PaperSubmission.id.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "submissions": submissions,
            "app_name": settings.app_name,
        },
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
