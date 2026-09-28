import json
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.analysis import Analysis
from backend.app.services.ai_service import AIService
from backend.app.services.document_processor import DocumentProcessor
from backend.app.services.ocr_service import OCRService
from backend.app.services.pdf_processor import PDFProcessor


router = APIRouter(
    prefix="/api/analyze",
    tags=["Analysis"]
)

document_processor = DocumentProcessor()
ai_service = AIService()
ocr_service = OCRService()
pdf_processor = PDFProcessor()


class TextAnalysisRequest(BaseModel):
    text: str


@router.post("/text")
def analyze_text(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db)
):
    try:
        processed_text = document_processor.process_text(
            request.text
        )

        report = ai_service.analyze_document(
            processed_text
        )

        analysis = Analysis(
            source_type="text",
            status="completed",
            summary=report.report_summary,
            report_json=report.model_dump_json(),
            extracted_text=processed_text
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "status": "success",
            "source_type": "text",
            "analysis_id": analysis.id,
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


@router.post("/image")
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Image file is required."
        )

    allowed_extensions = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
        ".tif",
    }

    extension = "." + file.filename.split(".")[-1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image format."
        )

    upload_path = None

    try:
        upload_path = f"backend/uploads/{file.filename}"

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )

        with open(upload_path, "wb") as uploaded_file:
            uploaded_file.write(contents)

        extracted_text = ocr_service.extract_text(
            upload_path
        )

        processed_text = document_processor.process_text(
            extracted_text
        )

        report = ai_service.analyze_document(
            processed_text
        )

        analysis = Analysis(
            source_type="image",
            filename=file.filename,
            status="completed",
            summary=report.report_summary,
            report_json=report.model_dump_json(),
            extracted_text=processed_text
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "status": "success",
            "source_type": "image",
            "analysis_id": analysis.id,
            "filename": file.filename,
            "extracted_text": processed_text,
            "report": report.model_dump()
        }

    except HTTPException:
        raise

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

    finally:
        if upload_path and os.path.exists(upload_path):
            os.remove(upload_path)


@router.post("/pdf")
async def analyze_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="PDF file is required."
        )

    extension = "." + file.filename.split(".")[-1].lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF."
        )

    upload_path = None

    try:
        upload_path = f"backend/uploads/{file.filename}"

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        with open(upload_path, "wb") as uploaded_file:
            uploaded_file.write(contents)

        extracted_text = pdf_processor.extract_text(
            upload_path
        )

        processed_text = document_processor.process_text(
            extracted_text
        )

        report = ai_service.analyze_document(
            processed_text
        )

        analysis = Analysis(
            source_type="pdf",
            filename=file.filename,
            status="completed",
            summary=report.report_summary,
            report_json=report.model_dump_json(),
            extracted_text=processed_text
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "status": "success",
            "source_type": "pdf",
            "analysis_id": analysis.id,
            "filename": file.filename,
            "extracted_text": processed_text,
            "report": report.model_dump()
        }

    except HTTPException:
        raise

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

    finally:
        if upload_path and os.path.exists(upload_path):
            os.remove(upload_path)


@router.get("/history")
def get_analysis_history(
    db: Session = Depends(get_db)
):
    analyses = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "count": len(analyses),
        "reports": [
            {
                "analysis_id": analysis.id,
                "source_type": analysis.source_type,
                "filename": analysis.filename,
                "status": analysis.status,
                "summary": analysis.summary,
                "created_at": analysis.created_at,
            }
            for analysis in analyses
        ],
    }


@router.get("/history/{analysis_id}")
def get_analysis_report(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    analysis = (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id)
        .first()
    )

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis report not found."
        )

    report = None

    if analysis.report_json:
        try:
            report = json.loads(analysis.report_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Stored clinical report is invalid."
            )

    return {
        "status": "success",
        "analysis_id": analysis.id,
        "source_type": analysis.source_type,
        "filename": analysis.filename,
        "analysis_status": analysis.status,
        "summary": analysis.summary,
        "extracted_text": analysis.extracted_text,
        "created_at": analysis.created_at,
        "report": report,
        "error_message": analysis.error_message,
    }