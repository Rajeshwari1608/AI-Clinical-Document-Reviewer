from pathlib import Path

import pytest

from backend.app.services.ocr_service import OCRService


SAMPLE_IMAGE = (
    Path(__file__).parent
    / "sample_data"
    / "synthetic_clinical_note.png"
)


def test_ocr_extracts_clinical_text():
    service = OCRService()

    result = service.extract_text(str(SAMPLE_IMAGE))

    assert "Ananya Kumar" in result
    assert "Fever" in result
    assert "38.5 C" in result
    assert "Paracetamol 500 mg" in result


def test_ocr_rejects_missing_file():
    service = OCRService()

    with pytest.raises(FileNotFoundError):
        service.extract_text("does_not_exist.png")


def test_ocr_rejects_unsupported_format(tmp_path):
    text_file = tmp_path / "sample.txt"
    text_file.write_text("Clinical note")

    service = OCRService()

    with pytest.raises(ValueError):
        service.extract_text(str(text_file))