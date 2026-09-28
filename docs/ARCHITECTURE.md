# System Architecture

# AI Clinical Document Reviewer

## 1. Architecture Overview

The AI Clinical Document Reviewer is implemented as a layered web application.

The system separates:

- Frontend presentation
- Backend API
- Document processing
- OCR
- AI/ML analysis
- Structured validation
- Database persistence
- External AI services

The frontend communicates with the backend through REST APIs. The backend is responsible for document processing, AI analysis, validation, persistence, and error handling.

---

# 2. High-Level Architecture

```text
                         USER
                          |
                          v
              +-----------------------+
              | React + Vite Frontend |
              |       TypeScript      |
              +-----------+-----------+
                          |
                          | HTTP / REST API
                          |
                          v
              +-----------------------+
              |     FastAPI Backend   |
              |        Python         |
              +-----------+-----------+
                          |
          +---------------+----------------+
          |               |                |
          v               v                v
 +----------------+ +-------------+ +-------------+
 | Document       | | OCR Service | | AI Service  |
 | Processor      | | Tesseract   | | Gemini API  |
 +-------+--------+ +------+------+ +------+------+
         |                 |               |
         |                 |               |
         +--------+--------+---------------+
                  |
                  v
          +------------------+
          | Structured Report|
          | Pydantic Models  |
          +--------+---------+
                   |
                   v
          +------------------+
          | SQLite Database  |
          |   SQLAlchemy     |
          +--------+---------+
                   |
                   v
          Previous Analyses

3. System Components

The application consists of the following major components:

Frontend
Backend API
Document Processor
OCR Service
PDF Processor
AI Service
Pydantic Schemas
Database
External AI Service

Each component has a separate responsibility.

4. Frontend
Technology

The frontend is implemented using:

React
TypeScript
Vite
Axios
CSS

The frontend is located in:

frontend/

Main frontend source files include:

frontend/
├── src/
│   ├── App.tsx
│   ├── App.css
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
Responsibilities

The frontend is responsible for:

Accepting clinical text
Accepting image uploads
Accepting PDF uploads
Sending requests to the backend
Displaying loading states
Displaying errors
Displaying structured reports
Displaying previous analyses
Opening previous reports

The frontend does not communicate directly with Gemini.

5. Backend
Technology

The backend is implemented using:

Python
FastAPI
SQLAlchemy
Pydantic

The backend is located in:

backend/

The backend provides the API layer between the frontend, document-processing services, AI service, and database.

6. Backend Structure

The backend follows a service-oriented structure.

backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── analysis.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   └── analysis.py
│   │
│   ├── schemas/
│   │   └── report_schema.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── document_processor.py
│   │   ├── ocr_service.py
│   │   └── pdf_processor.py
│   │
│   └── main.py
│
└── .env

The .env file contains environment-specific secrets and is excluded from Git.

7. API Layer

The FastAPI application exposes endpoints for clinical document analysis and report history.

The primary analysis endpoints are:

POST /api/analyze/text
POST /api/analyze/image
POST /api/analyze/pdf

History endpoints are:

GET /api/analyze/history
GET /api/analyze/history/{analysis_id}

The application also provides:

GET /
GET /health

for basic API availability and health checking.

8. Text Analysis Flow

The text-analysis workflow is:

User enters clinical text
          |
          v
React Frontend
          |
          | POST /api/analyze/text
          v
FastAPI
          |
          v
Create Processing Record
          |
          v
Document Processor
          |
          v
Normalized Clinical Text
          |
          v
AI Service
          |
          v
Gemini API
          |
          v
Structured JSON
          |
          v
Pydantic Validation
          |
          v
Database
          |
          v
FastAPI Response
          |
          v
React Frontend
          |
          v
Formatted Clinical Report
9. Image Analysis Flow

Image analysis uses OCR before AI processing.

User Uploads Image
        |
        v
React Frontend
        |
        | POST /api/analyze/image
        v
FastAPI
        |
        v
File Validation
        |
        v
Temporary File
        |
        v
OCR Service
        |
        v
Pillow
        |
        v
Tesseract OCR
        |
        v
Extracted Text
        |
        v
Document Processor
        |
        v
AI Service
        |
        v
Gemini API
        |
        v
Structured Report
        |
        v
Pydantic Validation
        |
        v
Database
        |
        v
Frontend

The temporary uploaded file is removed after processing.

10. PDF Analysis Flow

PDF analysis supports both text-based and scanned PDFs.

User Uploads PDF
        |
        v
React Frontend
        |
        | POST /api/analyze/pdf
        v
FastAPI
        |
        v
PDF Processor
        |
        v
pypdf Text Extraction
        |
        +----------------------+
        |                      |
   Text Found              No Text
        |                      |
        |                      v
        |                 PyMuPDF
        |                      |
        |                Render Pages
        |                      |
        |                 Tesseract OCR
        |                      |
        +----------+-----------+
                   |
                   v
             Extracted Text
                   |
                   v
          Document Processing
                   |
                   v
              AI Service
                   |
                   v
              Gemini API
                   |
                   v
          Structured Report
                   |
                   v
          Pydantic Validation
                   |
                   v
               Database
                   |
                   v
                Frontend
11. Document Processing Layer

The document-processing layer converts different document types into normalized text.

The main components are:

DocumentProcessor
OCRService
PDFProcessor
DocumentProcessor

Responsible for:

Validating text
Cleaning whitespace
Normalizing line endings
Removing empty lines
OCRService

Responsible for:

Validating image files
Opening images
Running Tesseract OCR
Returning extracted text
Reporting unreadable images
PDFProcessor

Responsible for:

Validating PDF files
Extracting text using pypdf
Rendering pages using PyMuPDF when required
Running OCR on scanned pages
Returning extracted text
12. AI/ML Layer

The AI service is implemented in:

backend/app/services/ai_service.py

The application uses Google's Gemini API.

The current model configuration is:

gemini-3.8-flash

The AI service receives normalized clinical text and generates a structured clinical report.

The AI layer is isolated from the frontend.

13. AI Processing Architecture
Normalized Clinical Text
          |
          v
     AI Service
          |
          v
  Source-Grounded Prompt
          |
          v
      Gemini API
          |
          v
 Structured JSON Response
          |
          v
 Pydantic Validation
          |
          v
 ClinicalReport Object

The AI service is responsible for requesting structured output rather than unrestricted natural-language output.

14. Structured Report Layer

The structured report is defined using Pydantic models.

The main model is:

ClinicalReport

It contains:

report_summary
primary_concerns
patient_info
symptoms
diagnoses
medications
vitals
allergies
observations
concerns
missing_information
inconsistencies
review_items

Nested Pydantic models are used for individual clinical entities.

This ensures that the backend receives predictable structured data.

15. AI Validation

AI-generated JSON is validated before it is stored.

The validation flow is:

Gemini Response
      |
      v
JSON Response
      |
      v
Pydantic Validation
      |
      +---- Valid ----> ClinicalReport
      |
      +---- Invalid --> Error

Invalid structured output is not treated as a successful analysis.

16. Database Layer

The application uses SQLite for local development.

SQLAlchemy is used as the database ORM.

The database configuration is located in:

backend/app/core/database.py

The database model is located in:

backend/app/models/analysis.py
17. Analysis Database Model

The Analysis model stores:

id
source_type
filename
status
summary
report_json
extracted_text
error_message
created_at

The database therefore stores both successful and failed analysis attempts.

18. Database Workflow

A new analysis begins with a processing record.

New Request
    |
    v
Create Analysis
status = processing
    |
    v
Process Document
    |
    v
Run AI
    |
    +----------+
    |          |
 Success     Failure
    |          |
    v          v
completed    failed
    |          |
    v          v
Save Report  Save Error
    |          |
    +-----+----+
          |
          v
      API Response

This allows failures to remain visible in the analysis history.

19. Persistence and History

Previous analyses can be retrieved through the history API.

GET /api/analyze/history

The history response contains information including:

Analysis ID
Source type
Filename
Status
Summary
Creation time
Error message when applicable

An individual report can be retrieved using:

GET /api/analyze/history/{analysis_id}

This allows the frontend to reopen previous analyses.

20. Error Handling Architecture

The backend handles failures at multiple layers.

                   Request
                      |
                      v
                Input Validation
                      |
             +--------+--------+
             |                 |
           Valid             Invalid
             |                 |
             v                 v
       Document Process      API Error
             |
             +----------------+
             |                |
          Success           Failure
             |                |
             v                v
          AI Service       API Error
             |
             +----------------+
             |                |
          Success           Failure
             |                |
             v                v
        Validation         Failed Record
             |
             +----------------+
             |                |
          Valid             Invalid
             |                |
             v                v
        Save Report        Failed Record

The system aims to return clear errors rather than exposing internal exceptions directly to the user.

21. Failure Persistence

Failed analyses are stored in the database.

For example:

status:
failed

error_message:
The PDF could not be processed using OCR.

This provides a history of failed attempts and prevents failures from disappearing without a record.

22. External Services

The primary external AI service is:

Google Gemini API

The backend communicates with Gemini using the google-genai package.

The Gemini API key is stored in the backend environment configuration.

The frontend does not contain the API key.

23. Security Boundary

The application keeps external service credentials on the backend.

                 Frontend
                     |
                     | API Request
                     v
                 Backend
                     |
                     | API Key
                     v
                Gemini API

The Gemini API key is not exposed to the browser.

The .env file is excluded from Git using .gitignore.

For production, additional security measures should be added, including authentication, authorization, HTTPS, secure secret management, and appropriate data protection.

24. Frontend-to-Backend Communication

The frontend uses Axios to communicate with the FastAPI backend.

The frontend backend URL is configured as:

http://127.0.0.1:8000

during local development.

Example request flow:

React
 |
 | Axios POST
 v
FastAPI
 |
 | JSON / multipart form data
 v
Backend Processing
 |
 | JSON Response
 v
React

Text analysis uses JSON request data.

Image and PDF analysis use multipart file uploads.

25. CORS

The FastAPI backend includes CORS middleware.

Local development origins are supported for:

localhost
127.0.0.1

This allows the Vite development frontend to communicate with the FastAPI backend during local development.

Production deployment should restrict allowed origins to the deployed frontend domain.

26. API Data Flow
Text
Frontend
   |
   | JSON
   v
POST /api/analyze/text
   |
   v
FastAPI
   |
   v
DocumentProcessor
   |
   v
AIService
   |
   v
ClinicalReport
   |
   v
Database
   |
   v
JSON Response
Image
Frontend
   |
   | Multipart File
   v
POST /api/analyze/image
   |
   v
FastAPI
   |
   v
OCRService
   |
   v
DocumentProcessor
   |
   v
AIService
   |
   v
ClinicalReport
   |
   v
Database
   |
   v
JSON Response
PDF
Frontend
   |
   | Multipart File
   v
POST /api/analyze/pdf
   |
   v
FastAPI
   |
   v
PDFProcessor
   |
   +---- pypdf
   |
   +---- PyMuPDF + Tesseract
   |
   v
DocumentProcessor
   |
   v
AIService
   |
   v
ClinicalReport
   |
   v
Database
   |
   v
JSON Response
27. Project Directory Structure

The main project structure is:

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
28. Component Responsibilities
Component	Responsibility
React Frontend	User interface and report presentation
Axios	Frontend-to-backend HTTP communication
FastAPI	REST API and request handling
DocumentProcessor	Text normalization
OCRService	Image OCR
PDFProcessor	PDF extraction and scanned PDF OCR
AIService	Gemini communication and report generation
Pydantic	Structured response validation
SQLAlchemy	Database ORM
SQLite	Local persistence
Tesseract	OCR engine
PyMuPDF	PDF page rendering
Gemini	AI-based clinical information extraction
29. End-to-End Architecture

The complete system can be represented as:

                         USER
                           |
                           v
                +---------------------+
                |   React Frontend    |
                | React + TypeScript  |
                |       + Vite        |
                +----------+----------+
                           |
                           | Axios
                           | REST API
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
30. Architecture Principles

The application follows these architectural principles:

Separation of Responsibilities

Each major component has a specific responsibility.

The frontend handles presentation, while the backend handles processing and AI communication.

Backend AI Isolation

The AI API is accessed only by the backend.

This protects API credentials and keeps AI logic separate from presentation logic.

Structured AI Output

The AI output is validated against a predefined schema before being used by the application.

Failure Visibility

Failures are returned to the frontend and persisted in the database where appropriate.

Extensibility

The service-based backend structure allows individual components to be replaced or extended.

For example:

SQLite can be replaced with PostgreSQL.
OCR can be improved or replaced.
The Gemini service can be abstracted for another AI provider.
Additional document formats can be added.
31. Local Development Architecture

During local development, the system runs as two services.

Frontend
http://localhost:5173
        |
        | HTTP
        v
Backend
http://127.0.0.1:8000
        |
        +---- SQLite
        |
        +---- Tesseract
        |
        +---- Gemini API

The frontend is started using:

npm run dev

The backend is started using:

python -m uvicorn backend.app.main:app --reload
32. Deployment Architecture

For production deployment, the architecture can be extended to:

                 Internet
                    |
                    v
            Deployed Frontend
                    |
                    v
             Backend API
                    |
          +---------+---------+
          |                   |
          v                   v
     PostgreSQL          Gemini API
          |
          v
    Analysis History

The exact deployment platform can be selected based on project requirements.

The production deployment should use:

HTTPS
Secure environment variables
Production database
Restricted CORS
Authentication where required
Appropriate logging
Error monitoring
33. Scalability Considerations

The current application is designed primarily for the internship assignment and local development.

For larger deployments, the following improvements could be introduced:

PostgreSQL
Object storage for uploaded documents
Background processing queues
Multiple backend instances
Containerized services
Load balancing
Centralized logging
Monitoring
AI request rate management
Caching where appropriate

The current service separation provides a foundation for these improvements.

34. Data Flow Summary

The complete data flow is:

Input Document
      |
      v
Frontend
      |
      v
FastAPI
      |
      v
Validation
      |
      v
Document Processing
      |
      v
OCR / PDF Extraction if Required
      |
      v
Normalized Clinical Text
      |
      v
Gemini AI
      |
      v
Structured Clinical Report
      |
      v
Pydantic Validation
      |
      v
Database Persistence
      |
      v
Frontend Presentation
35. Failure Flow Summary

The system handles failures at every major processing boundary.

Input
 |
 +-- Invalid Input ----------> Clear API Error
 |
 v
Document Processing
 |
 +-- Processing Failure -----> Failed Analysis
 |
 v
OCR / PDF Extraction
 |
 +-- Extraction Failure -----> Failed Analysis
 |
 v
Gemini AI
 |
 +-- API Failure ------------> Failed Analysis
 |
 v
Structured Output
 |
 +-- Validation Failure -----> Failed Analysis
 |
 v
Database
 |
 +-- Persistence Failure ----> API Error
 |
 v
Frontend
 |
 +-- Display Error ----------> User-visible Message
36. Architecture Summary

The AI Clinical Document Reviewer uses a layered architecture that separates user interaction, API handling, document processing, AI analysis, validation, and persistence.

The architecture supports:

Plain text clinical documents
Image-based clinical documents
Text-based PDFs
Scanned PDFs
OCR processing
AI-based structured extraction
Pydantic validation
Persistent analysis history
Failed-analysis tracking
Frontend report presentation

The separation between the frontend and backend ensures that AI credentials and processing logic remain on the server.

The separation between document processing and AI analysis also allows individual components to be improved independently.

This architecture provides a maintainable foundation for the current internship assignment and allows future extensions such as PostgreSQL, production deployment, authentication, improved OCR, monitoring, and scalable background processing.