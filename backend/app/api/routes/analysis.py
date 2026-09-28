from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.ai_service import AIService
from backend.app.services.document_processor import DocumentProcessor


router = APIRouter(
    prefix="/api/analyze",
    tags=["Analysis"]
)

document_processor = DocumentProcessor()
ai_service = AIService()


class TextAnalysisRequest(BaseModel):
    text: str


@router.post("/text")
def analyze_text(request: TextAnalysisRequest):
    try:
        processed_text = document_processor.process_text(
            request.text
        )

        report = ai_service.analyze_document(
            processed_text
        )

        return {
            "status": "success",
            "source_type": "text",
            "extracted_text": processed_text,
            "report": report.model_dump()
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )