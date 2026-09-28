from pathlib import Path

import pytesseract
from PIL import Image


class OCRService:
    """Extracts text from clinical images using Tesseract OCR."""

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("Image file was not found.")

        supported_formats = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}

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