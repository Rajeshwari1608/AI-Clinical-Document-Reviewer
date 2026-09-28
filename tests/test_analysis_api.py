import asyncio

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
from backend.app.schemas.report_schema import ClinicalReport


TEST_DATABASE_URL = "sqlite:///./test_clinical_reviewer.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def setup_test_database():
    Base.metadata.create_all(bind=test_engine)


def cleanup_test_database():
    Base.metadata.drop_all(bind=test_engine)


def get_test_db():
    return TestSessionLocal()


def create_fake_report(summary):
    return ClinicalReport(
        report_summary=summary,
        primary_concerns=["Fever"],
        patient_info={
            "name": "Ananya Kumar",
            "age": "45",
            "gender": None,
            "date": None,
        },
        symptoms=[
            {
                "name": "Fever",
                "details": "for three days",
            }
        ],
        diagnoses=[],
        medications=[],
        vitals=[],
        allergies=["No known allergies reported"],
        observations=[],
        concerns=[],
        missing_information=[],
        inconsistencies=[],
        review_items=[],
    )


def test_text_analysis_api_success(monkeypatch):
    setup_test_database()

    db = get_test_db()

    fake_report = create_fake_report(
        "Test clinical report."
    )

    def fake_analyze_document(text):
        return fake_report

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ai_service.analyze_document",
        fake_analyze_document,
    )

    request = TextAnalysisRequest(
        text="Patient Name: Ananya Kumar. Age: 45. Symptoms: Fever."
    )

    result = analyze_text(
        request,
        db=db
    )

    assert result["status"] == "success"
    assert result["source_type"] == "text"
    assert result["analysis_id"] is not None
    assert result["extracted_text"] == (
        "Patient Name: Ananya Kumar. Age: 45. Symptoms: Fever."
    )
    assert result["report"]["report_summary"] == (
        "Test clinical report."
    )

    saved_analysis = db.query(Analysis).first()

    assert saved_analysis is not None
    assert saved_analysis.source_type == "text"
    assert saved_analysis.status == "completed"
    assert saved_analysis.summary == "Test clinical report."

    db.close()
    cleanup_test_database()


def test_text_analysis_api_rejects_empty_input():
    setup_test_database()

    db = get_test_db()

    request = TextAnalysisRequest(text="   ")

    try:
        analyze_text(
            request,
            db=db
        )
        assert False, "Expected HTTPException"
    except Exception as error:
        assert error.status_code == 400
        assert "empty" in error.detail.lower()
    finally:
        db.close()
        cleanup_test_database()


def test_text_analysis_api_handles_ai_failure(monkeypatch):
    setup_test_database()

    db = get_test_db()

    def fake_analyze_document(text):
        raise RuntimeError(
            "Gemini clinical analysis failed."
        )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ai_service.analyze_document",
        fake_analyze_document,
    )

    request = TextAnalysisRequest(
        text="Patient Name: Ananya Kumar."
    )

    try:
        analyze_text(
            request,
            db=db
        )
        assert False, "Expected HTTPException"
    except Exception as error:
        assert error.status_code == 502
        assert error.detail == (
            "Gemini clinical analysis failed."
        )
    finally:
        db.close()
        cleanup_test_database()


def test_image_analysis_api_success(monkeypatch):
    setup_test_database()

    db = get_test_db()

    fake_report = create_fake_report(
        "Test image clinical report."
    )

    def fake_extract_text(file_path):
        return (
            "Patient Name: Ananya Kumar. "
            "Age: 45. Symptoms: Fever."
        )

    def fake_analyze_document(text):
        return fake_report

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ocr_service.extract_text",
        fake_extract_text,
    )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ai_service.analyze_document",
        fake_analyze_document,
    )

    class FakeFile:
        filename = "test.png"

        async def read(self):
            return b"fake image content"

    async def run_test():
        result = await analyze_image(
            FakeFile(),
            db=db
        )

        assert result["status"] == "success"
        assert result["source_type"] == "image"
        assert result["analysis_id"] is not None
        assert result["filename"] == "test.png"

        saved_analysis = db.query(Analysis).first()

        assert saved_analysis is not None
        assert saved_analysis.source_type == "image"
        assert saved_analysis.filename == "test.png"
        assert saved_analysis.status == "completed"

    asyncio.run(run_test())

    db.close()
    cleanup_test_database()


def test_pdf_analysis_api_success(monkeypatch):
    setup_test_database()

    db = get_test_db()

    fake_report = create_fake_report(
        "Test PDF clinical report."
    )

    def fake_extract_text(file_path):
        return (
            "Patient Name: Ananya Kumar. "
            "Age: 45. Symptoms: Fever."
        )

    def fake_analyze_document(text):
        return fake_report

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.pdf_processor.extract_text",
        fake_extract_text,
    )

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ai_service.analyze_document",
        fake_analyze_document,
    )

    class FakeFile:
        filename = "test.pdf"

        async def read(self):
            return b"fake pdf content"

    async def run_test():
        result = await analyze_pdf(
            FakeFile(),
            db=db
        )

        assert result["status"] == "success"
        assert result["source_type"] == "pdf"
        assert result["analysis_id"] is not None
        assert result["filename"] == "test.pdf"

        saved_analysis = db.query(Analysis).first()

        assert saved_analysis is not None
        assert saved_analysis.source_type == "pdf"
        assert saved_analysis.filename == "test.pdf"
        assert saved_analysis.status == "completed"

    asyncio.run(run_test())

    db.close()
    cleanup_test_database()


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

    result = get_analysis_history(db=db)

    assert result["status"] == "success"
    assert result["count"] == 2
    assert len(result["reports"]) == 2

    assert result["reports"][0]["summary"] == "Second report"
    assert result["reports"][1]["summary"] == "First report"
    
    db.close()
    cleanup_test_database()


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
    assert result["summary"] == "Stored clinical report."
    assert result["report"]["report_summary"] == (
        "Stored clinical report."
    )

    db.close()
    cleanup_test_database()


def test_get_analysis_report_not_found():
    setup_test_database()

    db = get_test_db()

    try:
        get_analysis_report(
            999999,
            db=db
        )
        assert False, "Expected HTTPException"
    except Exception as error:
        assert error.status_code == 404
        assert error.detail == "Analysis report not found."
    finally:
        db.close()
        cleanup_test_database()