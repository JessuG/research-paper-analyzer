from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PaperSubmission(Base):
    __tablename__ = "paper_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    abstract: Mapped[str] = mapped_column(Text)
    conclusion: Mapped[str] = mapped_column(Text)
    methodology: Mapped[str] = mapped_column(Text)
    findings: Mapped[str] = mapped_column(Text)
    research_gaps: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
