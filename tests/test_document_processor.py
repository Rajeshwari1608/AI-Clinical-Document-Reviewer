import pytest

from backend.app.services.document_processor import DocumentProcessor


def test_process_text_removes_extra_whitespace():
    processor = DocumentProcessor()

    text = """
    
    Patient: Ananya Kumar
    
    
    Symptoms: Fever, cough
    
    
    """

    result = processor.process_text(text)

    assert result == (
        "Patient: Ananya Kumar\n"
        "Symptoms: Fever, cough"
    )


def test_process_text_rejects_empty_text():
    processor = DocumentProcessor()

    with pytest.raises(ValueError):
        processor.process_text("")


def test_process_text_rejects_whitespace_only():
    processor = DocumentProcessor()

    with pytest.raises(ValueError):
        processor.process_text("   \n   ")
        