from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


OUTPUT_PATH = Path(__file__).parent / "sample_data" / "synthetic_clinical_note.pdf"


def create_pdf():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(OUTPUT_PATH), pagesize=A4)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "Synthetic Clinical Note")

    pdf.setFont("Helvetica", 11)

    lines = [
        "Patient Name: Ananya Kumar",
        "Age: 45",
        "Date: 2026-09-28",
        "",
        "Symptoms:",
        "Fever, cough, and fatigue for three days.",
        "",
        "Vital Signs:",
        "Temperature: 38.5 C",
        "Blood Pressure: 128/82 mmHg",
        "Heart Rate: 92 bpm",
        "",
        "Medication:",
        "Paracetamol 500 mg",
        "",
        "Allergies:",
        "No known allergies reported.",
    ]

    y = 760

    for line in lines:
        pdf.drawString(50, y, line)
        y -= 20

    pdf.save()

    print(f"Created: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_pdf()