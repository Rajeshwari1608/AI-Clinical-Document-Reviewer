from io import BytesIO
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image
from pypdf import PdfReader


class PDFProcessor:
    """Extracts text from normal and scanned PDF documents."""

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

        # Normal text-based PDF
        if extracted_text.strip():
            return extracted_text.strip()

        # Scanned PDF OCR fallback
        try:
            document = pymupdf.open(str(path))
            ocr_pages = []

            for page in document:
                pixmap = page.get_pixmap(dpi=200)
                image_bytes = pixmap.tobytes("png")

                image = Image.open(BytesIO(image_bytes))

                text = pytesseract.image_to_string(image)

                if text.strip():
                    ocr_pages.append(text.strip())

            document.close()

            ocr_text = "\n\n".join(
                page for page in ocr_pages if page
            )

        except Exception as error:
            raise ValueError(
                "The PDF could not be processed using OCR."
            ) from error

        if not ocr_text.strip():
            raise ValueError(
                "No readable text was found in this PDF. "
                "It may be scanned, handwritten, or unreadable."
            )

        return ocr_text.strip()