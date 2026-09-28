class DocumentProcessor:
    """Processes and normalizes clinical document text."""

    def process_text(self, text: str) -> str:
        """
        Clean and normalize plain text input.
        """

        if not text:
            raise ValueError("Document text cannot be empty.")

        # Remove leading/trailing whitespace
        cleaned_text = text.strip()

        if not cleaned_text:
            raise ValueError("Document text cannot be empty.")

        # Normalize line endings
        cleaned_text = cleaned_text.replace("\r\n", "\n")
        cleaned_text = cleaned_text.replace("\r", "\n")

        # Remove excessive blank lines
        lines = [
            line.strip()
            for line in cleaned_text.split("\n")
        ]

        cleaned_text = "\n".join(
            line for line in lines if line
        )

        return cleaned_text
    