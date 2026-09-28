from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.document_processor import DocumentProcessor


router = APIRouter(
    prefix="/api/analyze",
    tags=["Analysis"]
)

document_processor = DocumentProcessor()


class TextAnalysisRequest(BaseModel):
    text: str


@router.post("/text")
def analyze_text(request: TextAnalysisRequest):

    try:
        processed_text = document_processor.process_text(
            request.text
        )

        return {
            "status": "success",
            "source_type": "text",
            "extracted_text": processed_text
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )