import asyncio
import json

import backend.app.api.routes.analysis as analysis_module

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.api.routes.analysis import (
    TextAnalysisRequest,
    analyze_text,
    analyze_image,
    analyze_pdf,
    get_analysis_history,
    get_analysis_report,
)

from backend.app.core.database import Base
from backend.app.models.analysis import Analysis
from backend.app.schemas.report_schema import (
    ClinicalReport,
    PatientInfo,
    Symptom,
    Diagnosis,
    Medication,
    Vital,
    Observation,
    Concern,
    MissingInformation,
    Inconsistency,
    ReviewItem,
)


TEST_DATABASE_URL = "sqlite:///./test_clinical_reviewer.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def get_test_db():
    return TestingSessionLocal()


def create_fake_report(summary="Test clinical report."):
    return ClinicalReport(
        report_summary=summary,
        primary_concerns=["Fever"],
        patient_info=PatientInfo(
            name="Ananya Kumar",
            age="45",
            gender=None,
            date="2026-09-28"
        ),
        symptoms=[
            Symptom(
                name="Fever",
                details="For three days."
            )
        ],
        diagnoses=[],
        medications=[
            Medication(
                name="Paracetamol",
                dosage="500 mg",
                frequency=None,
                details=None
            )
        ],
        vitals=[
            Vital(
                name="Temperature",
                value="38.5",
                unit="C"
            )
        ],
        allergies=["No known allergies reported."],
        observations=[],
        concerns=[],
        missing_information=[],
        inconsistencies=[],
        review_items=[]
    )


def test_text_analysis_api_success():
    setup_test_database()
    db = get_test_db()

    original_ai_service = analysis_module.ai_service

    class FakeAIService:
        def analyze_document(self, text):
            return create_fake_report(
                "Patient has fever and cough."
            )

    analysis_module.ai_service = FakeAIService()

    try:
        request = TextAnalysisRequest(
            text="""
            Patient Name: Ananya Kumar.
            Age: 45.
            Symptoms: Fever and cough.
            """
        )

        result = analyze_text(
            request,
            db=db
        )

        assert result["status"] == "success"
        assert result["source_type"] == "text"
        assert result["analysis_id"] is not None
        assert result["report"]["report_summary"] == (
            "Patient has fever and cough."
        )

        saved_analysis = (
            db.query(Analysis)
            .filter(
                Analysis.id == result["analysis_id"]
            )
            .first()
        )

        assert saved_analysis is not None
        assert saved_analysis.status == "completed"
        assert saved_analysis.summary == (
            "Patient has fever and cough."
        )
        assert saved_analysis.extracted_text is not None

    finally:
        analysis_module.ai_service = original_ai_service
        db.close()


def test_text_analysis_api_rejects_empty_input():
    setup_test_database()
    db = get_test_db()

    request = TextAnalysisRequest(
        text=""
    )

    try:
        analyze_text(
            request,
            db=db
        )
        assert False

    except Exception as error:
        assert error.status_code == 400
        assert error.detail == (
            "Document text cannot be empty."
        )

    finally:
        db.close()


def test_text_analysis_api_handles_ai_failure():
    setup_test_database()
    db = get_test_db()

    original_ai_service = analysis_module.ai_service

    class FailingAIService:
        def analyze_document(self, text):
            raise RuntimeError(
                "AI service unavailable."
            )

    analysis_module.ai_service = FailingAIService()

    try:
        request = TextAnalysisRequest(
            text="Patient Name: Ananya Kumar."
        )

        try:
            analyze_text(
                request,
                db=db
            )
            assert False

        except Exception as error:
            assert error.status_code == 502
            assert error.detail == (
                "AI service unavailable."
            )

    finally:
        analysis_module.ai_service = original_ai_service
        db.close()


def test_image_analysis_api_success():
    setup_test_database()
    db = get_test_db()

    original_ocr_service = analysis_module.ocr_service
    original_ai_service = analysis_module.ai_service

    class FakeOCRService:
        def extract_text(self, file_path):
            return """
            Patient Name: Ananya Kumar.
            Age: 45.
            Symptoms: Fever and cough.
            """

    class FakeAIService:
        def analyze_document(self, text):
            return create_fake_report(
                "Image clinical report processed successfully."
            )

    analysis_module.ocr_service = FakeOCRService()
    analysis_module.ai_service = FakeAIService()

    class FakeUploadFile:
        filename = "synthetic_clinical_note.png"

        async def read(self):
            return b"fake image content"

    try:
        result = asyncio.run(
            analyze_image(
                file=FakeUploadFile(),
                db=db
            )
        )

        assert result["status"] == "success"
        assert result["source_type"] == "image"
        assert result["analysis_id"] is not None
        assert result["filename"] == (
            "synthetic_clinical_note.png"
        )

        saved_analysis = (
            db.query(Analysis)
            .filter(
                Analysis.id == result["analysis_id"]
            )
            .first()
        )

        assert saved_analysis is not None
        assert saved_analysis.status == "completed"
        assert saved_analysis.summary == (
            "Image clinical report processed successfully."
        )

    finally:
        analysis_module.ocr_service = original_ocr_service
        analysis_module.ai_service = original_ai_service
        db.close()


def test_pdf_analysis_api_success():
    setup_test_database()
    db = get_test_db()

    original_pdf_processor = analysis_module.pdf_processor
    original_ai_service = analysis_module.ai_service

    class FakePDFProcessor:
        def extract_text(self, file_path):
            return """
            Patient Name: Ananya Kumar.
            Age: 45.
            Symptoms: Fever and cough.
            """

    class FakeAIService:
        def analyze_document(self, text):
            return create_fake_report(
                "PDF clinical report processed successfully."
            )

    analysis_module.pdf_processor = FakePDFProcessor()
    analysis_module.ai_service = FakeAIService()

    class FakeUploadFile:
        filename = "synthetic_clinical_note.pdf"

        async def read(self):
            return b"fake pdf content"

    try:
        result = asyncio.run(
            analyze_pdf(
                file=FakeUploadFile(),
                db=db
            )
        )

        assert result["status"] == "success"
        assert result["source_type"] == "pdf"
        assert result["analysis_id"] is not None
        assert result["filename"] == (
            "synthetic_clinical_note.pdf"
        )

        saved_analysis = (
            db.query(Analysis)
            .filter(
                Analysis.id == result["analysis_id"]
            )
            .first()
        )

        assert saved_analysis is not None
        assert saved_analysis.status == "completed"
        assert saved_analysis.summary == (
            "PDF clinical report processed successfully."
        )

    finally:
        analysis_module.pdf_processor = original_pdf_processor
        analysis_module.ai_service = original_ai_service
        db.close()


def test_analysis_history_returns_saved_reports():
    setup_test_database()

    db = get_test_db()

    analysis_one = Analysis(
        source_type="text",
        status="completed",
        summary="First report",
        report_json="{}",
        extracted_text="First clinical note"
    )

    analysis_two = Analysis(
        source_type="pdf",
        filename="second.pdf",
        status="completed",
        summary="Second report",
        report_json="{}",
        extracted_text="Second clinical note"
    )

    db.add(analysis_one)
    db.add(analysis_two)
    db.commit()

    result = get_analysis_history(
        db=db
    )

    assert result["status"] == "success"
    assert result["count"] == 2
    assert len(result["reports"]) == 2

    assert result["reports"][0]["summary"] == (
        "Second report"
    )
    assert result["reports"][1]["summary"] == (
        "First report"
    )

    db.close()


def test_get_analysis_report_success():
    setup_test_database()

    db = get_test_db()

    fake_report = create_fake_report(
        "Stored clinical report."
    )

    analysis = Analysis(
        source_type="text",
        status="completed",
        summary=fake_report.report_summary,
        report_json=fake_report.model_dump_json(),
        extracted_text="Patient Name: Ananya Kumar."
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    result = get_analysis_report(
        analysis.id,
        db=db
    )

    assert result["status"] == "success"
    assert result["analysis_id"] == analysis.id
    assert result["source_type"] == "text"
    assert result["summary"] == (
        "Stored clinical report."
    )
    assert result["report"]["report_summary"] == (
        "Stored clinical report."
    )

    db.close()


def test_get_analysis_report_not_found():
    setup_test_database()

    db = get_test_db()

    try:
        get_analysis_report(
            999999,
            db=db
        )
        assert False

    except Exception as error:
        assert error.status_code == 404
        assert error.detail == (
            "Analysis report not found."
        )

    finally:
        db.close()


def test_text_analysis_persists_ai_failure():
    setup_test_database()

    db = get_test_db()

    original_ai_service = analysis_module.ai_service

    class FailingAIService:
        def analyze_document(self, text):
            raise RuntimeError(
                "AI service unavailable."
            )

    analysis_module.ai_service = FailingAIService()

    try:
        request = TextAnalysisRequest(
            text="Patient Name: Ananya Kumar."
        )

        try:
            analyze_text(
                request,
                db=db
            )
            assert False

        except Exception as error:
            assert error.status_code == 502
            assert error.detail == (
                "AI service unavailable."
            )

        failed_analysis = (
            db.query(Analysis)
            .order_by(Analysis.id.desc())
            .first()
        )

        assert failed_analysis is not None
        assert failed_analysis.status == "failed"
        assert failed_analysis.error_message == (
            "AI service unavailable."
        )
        assert failed_analysis.extracted_text == (
            "Patient Name: Ananya Kumar."
        )

    finally:
        analysis_module.ai_service = original_ai_service
        db.close()


def test_text_analysis_persists_empty_input_failure():
    setup_test_database()

    db = get_test_db()

    request = TextAnalysisRequest(
        text=""
    )

    try:
        analyze_text(
            request,
            db=db
        )
        assert False

    except Exception as error:
        assert error.status_code == 400
        assert error.detail == (
            "Document text cannot be empty."
        )

    failed_analysis = (
        db.query(Analysis)
        .order_by(Analysis.id.desc())
        .first()
    )

    assert failed_analysis is not None
    assert failed_analysis.status == "failed"
    assert failed_analysis.error_message == (
        "Document text cannot be empty."
    )

    db.close()


def test_image_analysis_rejects_unsupported_format():
    setup_test_database()

    db = get_test_db()

    class FakeUploadFile:
        filename = "clinical_note.txt"

    try:
        try:
            asyncio.run(
                analyze_image(
                    file=FakeUploadFile(),
                    db=db
                )
            )
            assert False

        except Exception as error:
            assert error.status_code == 400
            assert error.detail == (
                "Unsupported image format."
            )

    finally:
        db.close()


def test_pdf_analysis_rejects_unsupported_format():
    setup_test_database()

    db = get_test_db()

    class FakeUploadFile:
        filename = "clinical_note.txt"

    try:
        try:
            asyncio.run(
                analyze_pdf(
                    file=FakeUploadFile(),
                    db=db
                )
            )
            assert False

        except Exception as error:
            assert error.status_code == 400
            assert error.detail == (
                "Unsupported file format. Please upload a PDF."
            )

    finally:
        db.close()


def test_image_analysis_persists_ocr_failure():
    setup_test_database()

    db = get_test_db()

    original_ocr_service = analysis_module.ocr_service

    class FailingOCRService:
        def extract_text(self, file_path):
            raise ValueError(
                "The image could not be read or processed."
            )

    analysis_module.ocr_service = FailingOCRService()

    class FakeUploadFile:
        filename = "corrupt_clinical_note.png"

        async def read(self):
            return b"corrupt image content"

    try:
        try:
            asyncio.run(
                analyze_image(
                    file=FakeUploadFile(),
                    db=db
                )
            )
            assert False

        except Exception as error:
            assert error.status_code == 400
            assert error.detail == (
                "The image could not be read or processed."
            )

        failed_analysis = (
            db.query(Analysis)
            .order_by(Analysis.id.desc())
            .first()
        )

        assert failed_analysis is not None
        assert failed_analysis.status == "failed"
        assert failed_analysis.error_message == (
            "The image could not be read or processed."
        )

    finally:
        analysis_module.ocr_service = original_ocr_service
        db.close()


def test_pdf_analysis_persists_processing_failure():
    setup_test_database()

    db = get_test_db()

    original_pdf_processor = analysis_module.pdf_processor

    class FailingPDFProcessor:
        def extract_text(self, file_path):
            raise ValueError(
                "The PDF could not be opened or is corrupted."
            )

    analysis_module.pdf_processor = FailingPDFProcessor()

    class FakeUploadFile:
        filename = "corrupt_clinical_note.pdf"

        async def read(self):
            return b"corrupt pdf content"

    try:
        try:
            asyncio.run(
                analyze_pdf(
                    file=FakeUploadFile(),
                    db=db
                )
            )
            assert False

        except Exception as error:
            assert error.status_code == 400
            assert error.detail == (
                "The PDF could not be opened or is corrupted."
            )

        failed_analysis = (
            db.query(Analysis)
            .order_by(Analysis.id.desc())
            .first()
        )

        assert failed_analysis is not None
        assert failed_analysis.status == "failed"
        assert failed_analysis.error_message == (
            "The PDF could not be opened or is corrupted."
        )

    finally:
        analysis_module.pdf_processor = original_pdf_processor
        db.close()


def test_analysis_history_includes_failed_reports():
    setup_test_database()

    db = get_test_db()

    failed_analysis = Analysis(
        source_type="image",
        filename="corrupt.png",
        status="failed",
        summary=None,
        report_json=None,
        extracted_text=None,
        error_message="Image processing failed."
    )

    db.add(failed_analysis)
    db.commit()
    db.refresh(failed_analysis)

    result = get_analysis_history(
        db=db
    )

    assert result["status"] == "success"
    assert result["count"] == 1
    assert result["reports"][0]["status"] == "failed"
    assert result["reports"][0]["error_message"] == (
        "Image processing failed."
    )

    db.close()


def test_get_failed_analysis_report():
    setup_test_database()

    db = get_test_db()

    failed_analysis = Analysis(
        source_type="pdf",
        filename="corrupt.pdf",
        status="failed",
        summary=None,
        report_json=None,
        extracted_text=None,
        error_message="The PDF could not be processed."
    )

    db.add(failed_analysis)
    db.commit()
    db.refresh(failed_analysis)

    result = get_analysis_report(
        failed_analysis.id,
        db=db
    )

    assert result["status"] == "success"
    assert result["analysis_id"] == failed_analysis.id
    assert result["analysis_status"] == "failed"
    assert result["report"] is None
    assert result["error_message"] == (
        "The PDF could not be processed."
    )

    db.close()