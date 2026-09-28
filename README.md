Great. Paste this entire README.md into VS Code, replacing everything currently in the file.

# AI Clinical Document Reviewer

An AI-powered clinical document review system that accepts clinical information as plain text, images, and PDF documents, processes the document content, extracts structured clinical information, and presents the result as a readable clinical review report.

The application uses a React + TypeScript frontend, FastAPI backend, OCR/document-processing services, Gemini AI for structured clinical information extraction, Pydantic validation, and SQLite persistence during local development.

> **Important:** This project is intended for document review and information extraction. It is not an autonomous diagnostic system and should not replace professional clinical judgment.

---

## 1. Project Overview

The AI Clinical Document Reviewer provides an end-to-end workflow for reviewing clinical documents.

The system can:

- Accept clinical text directly
- Upload clinical images
- Upload PDF documents
- Extract text from normal PDFs
- Process scanned PDFs using OCR
- Extract text from clinical images using Tesseract OCR
- Analyze normalized clinical text using Gemini
- Generate a structured clinical report
- Identify missing or incomplete information
- Identify inconsistencies
- Identify concerns and review items
- Store completed analyses
- Store failed analyses with error information
- Display previous reports
- Reopen previous analyses through the frontend

The application separates frontend presentation, backend processing, document processing, AI analysis, validation, and database persistence.

---

# 2. Features

## Document Input

The application supports:

- Plain clinical text
- PNG images
- JPG images
- JPEG images
- BMP images
- TIF images
- TIFF images
- PDF documents

---

## Document Processing

The backend supports:

- Plain text normalization
- PDF text extraction
- Scanned PDF processing
- Image OCR
- PDF OCR fallback
- Empty-input validation
- Unsupported file validation
- Corrupt document handling
- Unreadable document handling

---

## AI Clinical Analysis

The AI service extracts:

- Report summary
- Primary concerns
- Patient information
- Symptoms
- Diagnoses / conditions
- Medications
- Vitals
- Allergies
- Observations
- Concerns
- Missing / incomplete information
- Inconsistencies
- Review items

The AI output is returned using a predefined structured schema.

---

## Report Presentation

The frontend presents the generated report in readable sections instead of displaying raw AI JSON.

The report contains:

- Clinical Review Report
- Report Summary
- Primary Concerns
- Patient Information
- Symptoms
- Diagnoses / Conditions
- Medications
- Vitals
- Allergies
- Observations
- Concerns
- Missing / Incomplete Information
- Inconsistencies
- Review Items

---

## Analysis History

Previous analyses are persisted in the database.

Users can:

- View previous analyses
- See the analysis status
- See the source type
- See the filename where applicable
- See the analysis timestamp
- See the report summary
- Open a previous report
- View failed analysis records

---

# 3. Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Axios
- CSS

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

## AI / ML

- Google Gemini API
- `google-genai`
- Structured JSON output
- Pydantic response validation

## Document Processing

- pypdf
- PyMuPDF
- Pillow

## OCR

- Tesseract OCR
- pytesseract

## Database

- SQLite
- SQLAlchemy

## Testing

- pytest

## Version Control

- Git
- GitHub

---

# 4. System Architecture

The application follows a layered architecture.

```text
                         USER
                           |
                           v
                +---------------------+
                |   React Frontend    |
                | React + TypeScript  |
                |       + Vite        |
                +----------+----------+
                           |
                           | Axios / REST API
                           v
                +---------------------+
                |    FastAPI Backend  |
                |       Python        |
                +----------+----------+
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
 +----------------+ +-------------+ +---------------+
 | Text Processor | | OCR Service | | PDF Processor |
 +----------------+ +------+------+ +-------+-------+
                           |                |
                           +-------+--------+
                                   |
                                   v
                         +------------------+
                         |  Normalized Text |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |    AI Service    |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         |   Gemini API     |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | Structured JSON  |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | Pydantic Schema  |
                         |    Validation    |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | SQLite Database  |
                         |    SQLAlchemy    |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | Analysis History |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | React Report UI  |
                         +------------------+

For more details, see:

docs/ARCHITECTURE.md

5. AI/ML Design

The AI/ML pipeline is:

User Input
    |
    +-------------------+
    |                   |
 Plain Text        Image / PDF
    |                   |
    |              Document Processing
    |                   |
    |              OCR / Text Extraction
    |                   |
    +---------+---------+
              |
       Normalized Text
              |
       Input Validation
              |
              v
       Gemini AI Service
              |
              v
      Structured JSON Output
              |
              v
       Pydantic Validation
              |
              v
      ClinicalReport Object
              |
              v
       Database Storage
              |
              v
        Frontend Display

The AI service uses Gemini to extract information from the supplied document.

The system is designed to reduce unsupported AI-generated information through:

Source-grounded extraction
Structured output
Pydantic validation
Explicit missing-information handling
Explicit concern and review fields
No unsupported diagnosis generation
Preservation of source values
Medication duplicate normalization

Detailed AI/ML design information is available in:

docs/AI_ML_DESIGN.md

6. Clinical Report Structure

The main structured report contains:

ClinicalReport
|
+-- report_summary
|
+-- primary_concerns
|
+-- patient_info
|
+-- symptoms
|
+-- diagnoses
|
+-- medications
|
+-- vitals
|
+-- allergies
|
+-- observations
|
+-- concerns
|
+-- missing_information
|
+-- inconsistencies
|
+-- review_items

The structured response is validated using Pydantic before it is treated as a successful report.

7. Project Structure
AI-Clinical-Document-Reviewer/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── analysis.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   │
│   │   ├── models/
│   │   │   └── analysis.py
│   │   │
│   │   ├── schemas/
│   │   │   └── report_schema.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── document_processor.py
│   │   │   ├── ocr_service.py
│   │   │   └── pdf_processor.py
│   │   │
│   │   └── main.py
│   │
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
│
├── tests/
│   ├── sample_data/
│   ├── create_sample_pdf.py
│   ├── create_scanned_pdf.py
│   ├── test_analysis_api.py
│   ├── test_ai_service.py
│   ├── test_document_processor.py
│   ├── test_ocr_service.py
│   └── test_pdf_processor.py
│
├── docs/
│   ├── AI_ML_DESIGN.md
│   └── ARCHITECTURE.md
│
├── .gitignore
└── README.md
8. Backend API

The backend provides the following main endpoints.

Health
GET /

Returns the API information message.

Health Check
GET /health

Returns:

{
  "status": "healthy"
}
Analyze Text
POST /api/analyze/text

Accepts clinical text as JSON.

Example:

{
  "text": "Patient Name: Ananya Kumar..."
}
Analyze Image
POST /api/analyze/image

Accepts an image file using multipart form data.

Supported image formats include:

PNG
JPG
JPEG
BMP
TIF
TIFF
Analyze PDF
POST /api/analyze/pdf

Accepts a PDF file using multipart form data.

Analysis History
GET /api/analyze/history

Returns previous analyses.

Individual Analysis
GET /api/analyze/history/{analysis_id}

Returns the selected analysis and its structured report.

9. Local Development Requirements

Before running the application locally, install:

Python
Node.js
npm
Git
Tesseract OCR

The backend requires a Gemini API key.

10. Tesseract OCR Setup

The application uses Tesseract OCR for image and scanned-PDF processing.

On Windows, install Tesseract OCR and ensure the executable is available to the Python OCR service.

The expected executable location used during development is:

C:\Program Files\Tesseract-OCR\tesseract.exe

If Tesseract is not available through the system PATH, configure the local environment so that pytesseract can access the executable.

11. Backend Setup

Open PowerShell in the project root.

Create a Python virtual environment:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install backend dependencies:

pip install -r .\backend\requirements.txt
12. Backend Environment Variables

Create:

backend/.env

The file should contain:

GEMINI_API_KEY=your_gemini_api_key

Replace the value with your own Gemini API key.

Do not commit the .env file to GitHub.

The .gitignore file excludes environment secrets from version control.

13. Start the Backend

From the project root, with the virtual environment activated:

python -m uvicorn backend.app.main:app --reload

The backend will be available locally at:

http://127.0.0.1:8000

FastAPI documentation is available at:

http://127.0.0.1:8000/docs
14. Frontend Setup

Open another PowerShell terminal.

Move to the frontend:

cd .\frontend

Install dependencies:

npm install

Start the Vite development server:

npm run dev

The frontend will normally be available at:

http://localhost:5173
15. Frontend Production Build

To create a production build:

npm run build

The generated frontend files are placed in:

frontend/dist/

The build process performs TypeScript compilation and Vite production bundling.

16. Database

The local development database uses SQLite.

The database configuration is:

sqlite:///./clinical_reviewer.db

SQLAlchemy manages database interactions.

The application automatically creates the required database tables when the backend starts.

The main database table is:

analyses
17. Database Fields

The analyses table contains:

Field	Description
id	Unique analysis identifier
source_type	Text, image, or PDF
filename	Uploaded filename where applicable
status	Processing, completed, or failed
summary	Report summary
report_json	Structured report JSON
extracted_text	Processed document text
error_message	Error information for failed analyses
created_at	Analysis creation timestamp
18. Running the Application

The complete local workflow requires two terminals.

Terminal 1 - Backend

From the project root:

.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --reload
Terminal 2 - Frontend
cd .\frontend
npm run dev

Then open:

http://localhost:5173
19. Using the Application
Text Analysis
Open the frontend.
Enter clinical information in the text area.
Click Analyze Document.
Wait for the AI analysis.
Review the generated clinical report.
The completed analysis is added to Previous Reports.
Image Analysis
Open the frontend.
Select an image file.
Click Analyze Document.
The backend processes the image using OCR.
Extracted text is sent to the AI service.
The structured report is returned to the frontend.
PDF Analysis
Open the frontend.
Select a PDF file.
Click Analyze Document.
The backend first attempts normal PDF text extraction.
If usable text is unavailable, OCR processing is used.
The extracted content is sent to Gemini.
The structured report is displayed.
20. Previous Reports

The application contains a Previous Reports section.

Each history item can display:

Filename or source type
Creation timestamp
Summary
Analysis status

Selecting a previous report retrieves the stored report from the backend.

21. Error Handling

The application handles common failure scenarios including:

Empty input
Unsupported file types
Missing files
Corrupt images
Corrupt PDFs
Unreadable images
PDFs without readable content
OCR failures
AI service failures
Invalid AI structured output
Database-related errors
Network/API failures

The backend stores failed analyses where appropriate and returns a user-readable error message.

22. Testing

The backend contains automated tests for the major processing components.

Tests cover:

Document processing
OCR
PDF processing
AI service
API success cases
API failure cases
Persistence
Analysis history
Individual report retrieval
Unsupported formats
Processing failures
Structured AI response validation

Run the backend tests from the project root using:

python -m pytest

The current backend test suite contains:

29 tests
23. Synthetic Clinical Data

The project uses synthetic clinical information for development and demonstration.

Example synthetic patient data includes:

Patient Name: Ananya Kumar
Age: 45
Date: 2026-09-28

Symptoms:
Fever, cough, and fatigue for three days.

Vitals:
Temperature: 38.5 C
Blood Pressure: 128/82 mmHg
Heart Rate: 92 bpm

Medication:
Paracetamol 500 mg

Allergies:
No known allergies reported.

The project should not use real patient information for demonstrations or testing.

24. Reliability

The application is designed to handle failures at multiple stages.

Input
 |
 v
Validation
 |
 v
Document Processing
 |
 v
OCR / PDF Extraction
 |
 v
AI Analysis
 |
 v
Structured Validation
 |
 v
Database Persistence
 |
 v
Frontend

Failures at these stages are handled rather than silently ignored.

Failed analyses are persisted with an appropriate status and error message where possible.

25. Security

The application keeps the Gemini API key on the backend.

The frontend does not contain the Gemini API key.

The environment file:

backend/.env

must not be committed to GitHub.

The project .gitignore is configured to exclude environment secrets and development-generated files.

For production deployment, additional security controls should be implemented, including:

HTTPS
Authentication
Authorization
Secure secret management
Restricted CORS
Audit logging
Encryption
Data retention controls
26. Limitations

The current implementation has several limitations.

OCR

OCR quality depends on the quality of the uploaded document.

Poor-quality or handwritten documents may produce incomplete text.

AI

AI analysis depends on:

Source document quality
Completeness of the source information
Gemini API availability
API quotas and limits
Clinical Interpretation

The system performs document review and structured information extraction.

It should not be treated as an autonomous diagnostic system.

Database

SQLite is used for local development.

A production deployment should use a production-grade database such as PostgreSQL.

Authentication

The current local development implementation does not provide a complete production authentication and authorization system.

27. Future Improvements

Potential future improvements include:

PostgreSQL production database
Authentication and authorization
Secure user accounts
Better handwriting recognition
Improved medical OCR
Confidence scores
Document-quality scoring
Medical terminology normalization
Human-in-the-loop review
Production monitoring
Audit logging
Containerized deployment
Background document processing
Scalable cloud deployment
Additional document formats
Improved AI validation
Multi-model verification
28. Documentation

Additional technical documentation is available in the docs directory.

System Architecture

docs/ARCHITECTURE.md

Contains:

High-level architecture
Component responsibilities
API flow
Text workflow
Image workflow
PDF workflow
Database architecture
AI architecture
Error handling
Deployment architecture
AI/ML Design

docs/AI_ML_DESIGN.md

Contains:

AI/ML pipeline
Document processing
OCR
PDF processing
Gemini integration
Structured output
Pydantic validation
Missing information handling
Hallucination reduction
AI failure handling
Design decisions
Limitations
Future improvements
29. Development Commands
Activate Python Environment
.\.venv\Scripts\Activate.ps1
Start Backend
python -m uvicorn backend.app.main:app --reload
Install Frontend Dependencies
cd .\frontend
npm install
Start Frontend
npm run dev
Build Frontend
npm run build
Run Backend Tests

From the project root:

python -m pytest
30. Git Workflow

The project uses Git for version control.

Typical workflow:

git status
git add .
git commit -m "Describe the change"
git push

The repository should not contain:

API keys
.env files
Real clinical data
Generated local databases
Temporary uploaded documents
31. Deployment

The application is designed for deployment as separate frontend and backend services.

A production architecture can use:

                    Internet
                       |
                       v
               Deployed Frontend
                       |
                       v
                Backend API
                  /       \
                 /         \
                v           v
        Production DB    Gemini API

The production environment should configure:

Frontend URL
Backend URL
Gemini API key
Production database
CORS allowed origins
HTTPS
Secure environment variables

The live deployment URLs should be added to this README after deployment.

32. Live URLs
Frontend
Not deployed yet
Backend API
Not deployed yet
API Documentation
Not deployed yet

These values should be updated after the application is deployed.

33. Screenshots

Screenshots of the following application screens should be added before final submission:

Main application screen
Text analysis input
Generated clinical report
Image upload workflow
PDF upload workflow
Previous Reports section
Error handling example
FastAPI API documentation

Recommended location:

docs/screenshots/

The README can then reference the screenshots.

34. Repository

GitHub repository:

https://github.com/Rajeshwari1608/AI-Clinical-Document-Reviewer
35. Submission Checklist

Before final submission, verify:

 Frontend works
 Backend works
 Text analysis works
 Image analysis works
 PDF analysis works
 Scanned PDF processing works
 Previous reports work
 Failed analyses are persisted
 Error messages are displayed
 Backend tests pass
 Frontend production build passes
 .env is not committed
 Only synthetic clinical data is used
 Architecture documentation is complete
 AI/ML documentation is complete
 Screenshots are added
 Deployment is completed
 Live frontend URL is added
 Live backend URL is added
 Repository is up to date
36. Project Status

The current implementation includes:

React + Vite frontend
FastAPI backend
SQLite persistence
Plain text analysis
Image OCR
PDF text extraction
Scanned PDF OCR
Gemini AI analysis
Structured Pydantic reports
Missing information handling
Inconsistency handling
Review item handling
Analysis history
Failed analysis persistence
Backend automated tests
Frontend production build
Architecture documentation
AI/ML design documentation