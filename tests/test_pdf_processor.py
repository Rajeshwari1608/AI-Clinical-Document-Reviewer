from pathlib import Path

import pytest

from backend.app.services.pdf_processor import PDFProcessor


SAMPLE_PDF = (
    Path(__file__).parent
    / "sample_data"
    / "synthetic_clinical_note.pdf"
)


def test_pdf_processor_extracts_text():
    processor = PDFProcessor()

    result = processor.extract_text(str(SAMPLE_PDF))

    assert "Ananya Kumar" in result
    assert "Fever, cough, and fatigue" in result
    assert "38.5 C" in result


def test_pdf_processor_rejects_missing_file():
    processor = PDFProcessor()

    with pytest.raises(FileNotFoundError):
        processor.extract_text("does_not_exist.pdf")


def test_pdf_processor_rejects_non_pdf_file(tmp_path):
    text_file = tmp_path / "sample.txt"
    text_file.write_text("Clinical note")

    processor = PDFProcessor()

    with pytest.raises(ValueError):
        processor.extract_text(str(text_file))
