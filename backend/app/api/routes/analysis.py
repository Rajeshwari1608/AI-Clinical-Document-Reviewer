import os

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

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


@router.post("/image")
async def analyze_image(
    file: UploadFile = File(...)
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

        return {
            "status": "success",
            "source_type": "image",
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
    file: UploadFile = File(...)
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

        return {
            "status": "success",
            "source_type": "pdf",
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