import pytest

from backend.app.services.ai_service import AIService


SAMPLE_CLINICAL_TEXT = """
Patient Name: Ananya Kumar.
Age: 45.
Symptoms: Fever, cough, and fatigue for three days.
Vitals: Temperature 38.5 C, BP 128/82 mmHg, HR 92 bpm.
Medication: Paracetamol 500 mg.
Allergies: No known allergies reported.
"""


class FakeInteraction:
    def __init__(self, output_text):
        self.output_text = output_text


def test_ai_service_rejects_empty_text():
    service = AIService()

    with pytest.raises(ValueError, match="cannot be empty"):
        service.analyze_document("")


def test_ai_service_returns_structured_report(monkeypatch):
    service = AIService()

    fake_response = FakeInteraction(
        """
        {
          "report_summary": "Clinical note for Ananya Kumar.",
          "primary_concerns": ["Fever", "Cough"],
          "patient_info": {
            "name": "Ananya Kumar",
            "age": "45",
            "gender": null,
            "date": null
          },
          "symptoms": [
            {
              "name": "Fever",
              "details": "for three days"
            },
            {
              "name": "Cough",
              "details": "for three days"
            }
          ],
          "diagnoses": [],
          "medications": [
            {
              "name": "Paracetamol",
              "dosage": "500 mg",
              "frequency": null,
              "details": null
            }
          ],
          "vitals": [
            {
              "name": "Temperature",
              "value": "38.5",
              "unit": "C"
            }
          ],
          "allergies": [
            "No known allergies reported"
          ],
          "observations": [],
          "concerns": [],
          "missing_information": [],
          "inconsistencies": [],
          "review_items": []
        }
        """
    )

    def fake_create(*args, **kwargs):
        return fake_response

    monkeypatch.setattr(
        service.client.interactions,
        "create",
        fake_create
    )

    report = service.analyze_document(SAMPLE_CLINICAL_TEXT)

    assert report.patient_info.name == "Ananya Kumar"
    assert report.patient_info.age == "45"
    assert len(report.symptoms) == 2
    assert report.medications[0].name == "Paracetamol"
    assert report.medications[0].dosage == "500 mg"
    assert report.allergies == ["No known allergies reported"]


def test_ai_service_rejects_invalid_structured_output(monkeypatch):
    service = AIService()

    fake_response = FakeInteraction(
        '{"invalid": "clinical report"}'
    )

    def fake_create(*args, **kwargs):
        return fake_response

    monkeypatch.setattr(
        service.client.interactions,
        "create",
        fake_create
    )

    with pytest.raises(ValueError):
        service.analyze_document(SAMPLE_CLINICAL_TEXT)


def test_ai_service_handles_gemini_failure(monkeypatch):
    service = AIService()

    def fake_create(*args, **kwargs):
        raise Exception("Gemini API unavailable")

    monkeypatch.setattr(
        service.client.interactions,
        "create",
        fake_create
    )

    with pytest.raises(RuntimeError, match="Gemini clinical analysis failed"):
        service.analyze_document(SAMPLE_CLINICAL_TEXT)