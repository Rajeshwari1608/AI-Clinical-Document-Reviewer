from backend.app.api.routes.analysis import (
    TextAnalysisRequest,
    analyze_text,
)
from backend.app.schemas.report_schema import ClinicalReport


def test_text_analysis_api_success(monkeypatch):
    fake_report = ClinicalReport(
        report_summary="Test clinical report.",
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

    def fake_analyze_document(text):
        return fake_report

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ai_service.analyze_document",
        fake_analyze_document,
    )

    request = TextAnalysisRequest(
        text="Patient Name: Ananya Kumar. Age: 45. Symptoms: Fever."
    )

    result = analyze_text(request)

    assert result["status"] == "success"
    assert result["source_type"] == "text"
    assert result["extracted_text"] == (
        "Patient Name: Ananya Kumar. Age: 45. Symptoms: Fever."
    )
    assert result["report"]["report_summary"] == "Test clinical report."


def test_text_analysis_api_rejects_empty_input():
    request = TextAnalysisRequest(text="   ")

    try:
        analyze_text(request)
        assert False, "Expected HTTPException"
    except Exception as error:
        assert error.status_code == 400
        assert "empty" in error.detail.lower()


def test_text_analysis_api_handles_ai_failure(monkeypatch):
    def fake_analyze_document(text):
        raise RuntimeError("Gemini clinical analysis failed.")

    monkeypatch.setattr(
        "backend.app.api.routes.analysis.ai_service.analyze_document",
        fake_analyze_document,
    )

    request = TextAnalysisRequest(
        text="Patient Name: Ananya Kumar."
    )

    try:
        analyze_text(request)
        assert False, "Expected HTTPException"
    except Exception as error:
        assert error.status_code == 502
        assert error.detail == "Gemini clinical analysis failed."