import os
from pathlib import Path

import pytesseract
from PIL import Image


def configure_tesseract() -> None:
    """Configure Tesseract for local Windows and deployed environments."""

    configured_path = os.getenv("TESSERACT_CMD")

    if configured_path and Path(configured_path).exists():
        pytesseract.pytesseract.tesseract_cmd = configured_path
        return

    windows_path = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if windows_path.exists():
        pytesseract.pytesseract.tesseract_cmd = str(windows_path)
        return

    pytesseract.pytesseract.tesseract_cmd = "tesseract"


configure_tesseract()


class OCRService:
    """Extracts text from clinical images using Tesseract OCR."""

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("Image file was not found.")

        supported_formats = {
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tiff",
            ".tif",
        }

        if path.suffix.lower() not in supported_formats:
            raise ValueError("Unsupported image format.")

        try:
            image = Image.open(path)
            image.verify()

            image = Image.open(path)
            extracted_text = pytesseract.image_to_string(image)

        except Exception as error:
            raise ValueError(
                "The image could not be read or processed."
            ) from error

        extracted_text = extracted_text.strip()

        if not extracted_text:
            raise ValueError(
                "No readable text was found in the image. "
                "The image may be blank, handwritten, or too low quality."
            )

        return extracted_text