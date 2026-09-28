from google import genai

from backend.app.core.config import settings
from backend.app.schemas.report_schema import ClinicalReport


class AIService:
    """Generates structured clinical reports using Gemini."""

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )
        self.model = "gemini-3.8-flash"

    def analyze_document(self, text: str) -> ClinicalReport:
        if not text or not text.strip():
            raise ValueError(
                "Clinical document text cannot be empty."
            )

        prompt = f"""
You are an AI clinical document reviewer performing STRICT
information extraction from a synthetic clinical document.

Your task is to extract information exactly as written in the
document and return it in the required structured schema.

CRITICAL EXTRACTION RULES:

1. Extract information ONLY from the clinical document.
2. NEVER invent, modify, expand, or guess information.
3. Preserve patient names exactly as written.
4. Preserve numerical values exactly as written whenever possible.
5. If a field is not present, return null for that field.
6. If a list has no items, return an empty list [].
7. Every required field in the schema must be present.
8. Extract EVERY explicitly stated symptom.
9. Extract EVERY explicitly stated medication, including dosage,
   frequency, and details when available.
10. Extract EVERY explicitly stated vital sign.
11. Extract explicitly stated allergies.
12. If the document says "No known allergies", preserve that
    information in the allergies field.
13. Extract patient name, age, gender, and date when explicitly stated.
14. Do NOT infer a diagnosis from symptoms or vital signs.
15. Only report a diagnosis if the document explicitly states it.
16. Only identify inconsistencies when the document contains
    genuinely conflicting information.
17. Put genuinely missing important information under
    missing_information.
18. Put unclear or potentially unreliable information under
    concerns or review_items.
19. This is clinical document review and information extraction,
    NOT medical diagnosis.

IMPORTANT:
The source text is authoritative. Do not add words to names,
medications, diagnoses, symptoms, or other extracted values.

Clinical document:

{text}
"""

        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt,
                response_format={
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": ClinicalReport.model_json_schema(),
                },
            )

            if not interaction.output_text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            report = ClinicalReport.model_validate_json(
                interaction.output_text
            )

            # Remove duplicate medications while preserving
            # the first occurrence.
            unique_medications = {}
            for medication in report.medications:
                key = (
                    medication.name.lower(),
                    (medication.dosage or "").lower(),
                    (medication.frequency or "").lower(),
                )
                unique_medications[key] = medication

            report.medications = list(unique_medications.values())

            return report

        except ValueError:
            raise

        except Exception as error:
            raise RuntimeError(
                f"Gemini clinical analysis failed: {error}"
            ) from error