from pathlib import Path

from pypdf import PdfReader


class PDFProcessor:
    """Extracts text from PDF documents."""

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("PDF file was not found.")

        if path.suffix.lower() != ".pdf":
            raise ValueError("The uploaded file is not a PDF.")

        try:
            reader = PdfReader(str(path))
        except Exception as error:
            raise ValueError(
                "The PDF could not be opened or is corrupted."
            ) from error

        extracted_pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                extracted_pages.append(text.strip())

        extracted_text = "\n\n".join(
            page for page in extracted_pages if page
        )

        if not extracted_text.strip():
            raise ValueError(
                "No readable text was found in this PDF. "
                "It may be scanned, handwritten, or unreadable."
            )

        return extracted_text.strip()