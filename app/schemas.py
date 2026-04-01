from pydantic import BaseModel, Field


class PaperSubmissionCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    abstract: str = Field(..., min_length=30)
    conclusion: str = Field(..., min_length=20)
