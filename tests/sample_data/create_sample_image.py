from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT_PATH = (
    Path(__file__).parent / "synthetic_clinical_note.png"
)


def create_clinical_image():
    width = 1400
    height = 900

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 32)
        title_font = ImageFont.truetype("arialbd.ttf", 42)
    except OSError:
        font = ImageFont.load_default()
        title_font = font

    lines = [
        "CLINICAL NOTE",
        "",
        "Patient Name: Ananya Kumar",
        "Age: 45",
        "Date: 2026-09-28",
        "",
        "Symptoms: Fever, cough, and fatigue for three days.",
        "",
        "Vitals:",
        "Temperature: 38.5 C",
        "Blood Pressure: 128/82 mmHg",
        "Heart Rate: 92 bpm",
        "",
        "Medication: Paracetamol 500 mg",
        "Allergies: No known allergies reported.",
    ]

    y = 60

    for index, line in enumerate(lines):
        current_font = title_font if index == 0 else font
        draw.text((60, y), line, fill="black", font=current_font)
        y += 55

    image.save(OUTPUT_PATH)

    print(f"Created: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_clinical_image()