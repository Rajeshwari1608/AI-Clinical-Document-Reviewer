# AI/ML Design – AI Clinical Document Reviewer

## 1. Overview

The AI Clinical Document Reviewer is an AI-powered application that accepts clinical information as plain text, images, and PDF documents.

The system processes the input, extracts clinical information, sends the normalized clinical text to a Gemini AI service, validates the generated response against a predefined Pydantic schema, and presents the result as a structured clinical review.

The system is designed for document review and information extraction. It does not replace clinical judgment or provide independent medical diagnosis.

---

## 2. AI/ML Pipeline

The overall pipeline is:

```text
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
        Gemini AI Service
              |
      Structured JSON Output
              |
       Pydantic Validation
              |
     Duplicate Normalization
              |
      ClinicalReport Object
              |
        Database Storage
              |
        Frontend Display

The AI service is separated from the frontend and API routing layer.

The frontend communicates with the FastAPI backend, while the backend is responsible for document processing, AI communication, validation, and persistence.

3. Input Types

The application supports three primary input types.

3.1 Plain Text

Users can directly enter clinical information into the frontend.

Examples include:

Clinical notes
Patient symptoms
Medication information
Vital signs
Diagnoses
Allergy information
Clinical observations

The submitted text is sent to the backend through the text analysis API.

3.2 Image

Users can upload clinical images.

Supported image formats include:

PNG
JPG
JPEG
BMP
TIF
TIFF

The backend validates the uploaded image and uses OCR to extract readable text.

3.3 PDF

Users can upload PDF documents.

The PDF processor supports:

Text-based PDFs
Scanned PDFs

For normal PDFs, text is first extracted directly.

If usable text is not available, the system uses an OCR fallback process.

4. Document Processing Pipeline

The document processing layer converts different input types into normalized clinical text.

Input
  |
  +---- Plain Text
  |        |
  |        v
  |   Text Processor
  |
  +---- Image
  |        |
  |        v
  |    Tesseract OCR
  |
  +---- PDF
           |
           +---- Text Extraction
           |
           +---- OCR Fallback
                    |
                    v
             Extracted Text
                    |
                    v
             Normalized Text

The objective of this layer is to provide the AI service with readable clinical text regardless of the original input format.

5. Plain Text Processing

Plain text processing is implemented through the document processor.

The processor performs basic normalization.

The processing steps are:

Validate that the text is not empty.
Remove leading and trailing whitespace.
Normalize Windows and Unix line endings.
Remove unnecessary empty lines.
Return cleaned clinical text.

Empty input is rejected before it reaches the AI service.

This prevents unnecessary AI requests and provides an immediate validation error to the user.

6. Image OCR Processing

Image processing is implemented using:

Pillow
pytesseract
Tesseract OCR

The processing pipeline is:

Uploaded Image
      |
      v
File Validation
      |
      v
Pillow Validation
      |
      v
Tesseract OCR
      |
      v
Extracted Text
      |
      v
Clinical Text Processing
      |
      v
Gemini AI

The OCR service verifies that the uploaded file is readable before extracting text.

If the image cannot be opened or processed, an error is returned.

If no readable text is detected, the system reports that the image may be:

Blank
Handwritten
Too low quality
Otherwise unreadable

The system does not attempt to invent content when OCR produces no readable information.

7. PDF Processing

PDF processing is implemented using:

pypdf
PyMuPDF
Pillow
Tesseract OCR

The system first attempts normal text extraction.

PDF
 |
 v
pypdf
 |
 +---- Text Found ----> Extracted Text
 |
 +---- No Text
          |
          v
       PyMuPDF
          |
          v
     Render PDF Pages
          |
          v
       Page Images
          |
          v
     Tesseract OCR
          |
          v
     Extracted Text

This approach allows the application to handle both digitally generated and scanned PDF documents.

8. AI Service

The AI service is implemented in:

backend/app/services/ai_service.py

The application uses Google's Gemini API through the google-genai Python package.

The configured model is:

gemini-3.8-flash

The AI service is responsible for:

Receiving normalized clinical text
Constructing the extraction prompt
Calling the Gemini API
Requesting structured output
Validating the returned JSON
Normalizing duplicate medication entries
Returning the validated clinical report

The AI service is kept separate from the frontend and API routing logic.

9. AI Extraction Objective

The AI model is used primarily for clinical information extraction and structured document review.

The model is instructed to extract information supported by the source document.

The report contains:

Report summary
Primary concerns
Patient information
Symptoms
Diagnoses
Medications
Vitals
Allergies
Observations
Concerns
Missing information
Inconsistencies
Review items

The model is not instructed to independently diagnose a patient.

10. Structured AI Output

The AI response is requested in a predefined structured format.

The primary schema is:

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

The schema is implemented using Pydantic models.

This provides a consistent contract between the AI service and the rest of the backend.

11. Clinical Report Schema

The main report contains the following fields.

Report Summary

A concise summary of the information contained in the document.

Primary Concerns

Important concerns identified from the source document.

Patient Information

Includes:

Name
Age
Gender
Date
Symptoms

Each symptom can contain:

Name
Details
Diagnoses

Each diagnosis or condition can contain:

Condition
Details
Medications

Each medication can contain:

Name
Dosage
Frequency
Details
Vitals

Each vital can contain:

Name
Value
Unit
Allergies

A list of allergy information found in the document.

Observations

Clinical observations extracted from the document.

Concerns

Information that may require attention or clarification.

Missing Information

Information that is expected or relevant but is not available in the source document.

Inconsistencies

Conflicting or inconsistent information explicitly identified in the source document.

Review Items

Items that may require additional human review.

12. Pydantic Validation

The structured AI response is validated using Pydantic.

The main validation operation is:

ClinicalReport.model_validate_json(interaction.output_text)

This provides a validation boundary between external AI output and application data.

If the returned response does not match the expected structure, the response is rejected rather than being stored as a successful clinical report.

13. Missing Information Handling

Missing information is explicitly represented in the report.

The AI is instructed not to invent information that is absent from the source document.

For example, if a clinical document contains:

Patient Name: Ananya Kumar
Age: 45

but does not contain gender, the system should not guess the patient's gender.

Instead, the missing information can be represented as:

missing_information:
    Gender

The system therefore distinguishes between:

Information present in the document
Information missing from the document
Information that requires review

This is important for reducing unsupported assumptions.

14. Handling Unclear Information

Clinical documents may contain information that is difficult to interpret.

Examples include:

Poor OCR output
Unclear text
Incomplete information
Potentially unreliable document sections
Information requiring clarification

The system uses the following fields to surface such information:

concerns
review_items

Instead of silently interpreting uncertain information, the system can identify it for further review.

15. Hallucination Reduction

The application uses several mechanisms to reduce unsupported AI-generated information.

15.1 Source-Grounded Prompt

The AI prompt instructs the model to use only the supplied clinical document as the source of information.

The model is instructed not to invent:

Patient names
Ages
Diagnoses
Medications
Symptoms
Vitals
Allergies
Numerical values
15.2 No Unsupported Diagnosis

The system does not ask the model to create a diagnosis from symptoms.

Diagnoses and conditions should only be reported when supported by the supplied document.

15.3 Preserve Source Values

The model is instructed to preserve names and numerical values from the source document.

For example, if a document states:

Temperature: 38.5 C

the system should preserve the value rather than modifying it.

15.4 Explicit Missing Information

When information is unavailable, the system uses missing-information fields rather than generating a value.

Scalar fields can use:

null

and list fields can be empty:

[]

when appropriate.

15.5 Structured Validation

The response must match the predefined Pydantic schema.

Malformed output is rejected.

15.6 Human Review Fields

Potentially incomplete or uncertain information can be surfaced through:

concerns
missing_information
inconsistencies
review_items

This makes uncertainty visible instead of hiding it.

16. Medication Deduplication

The AI service includes a final normalization step for medication entries.

Medication entries are compared using:

Medication name
Dosage
Frequency

The comparison is normalized to lowercase.

This prevents identical medication records from appearing multiple times in the final report.

For example:

Paracetamol 500 mg
Paracetamol 500 mg

can be represented as one medication entry when the dosage and frequency information are equivalent.

17. AI Failure Handling

The AI service is an external dependency and can fail.

Potential failures include:

API connection errors
Rate limits
API quota exhaustion
Empty AI responses
Invalid structured responses
External service failures

These failures are handled by the backend.

The application does not treat an unsuccessful AI request as a successful clinical analysis.

18. Invalid Structured Output Handling

If Gemini returns a response that does not conform to the expected structure, the backend rejects the response.

For example, if a required field is missing or the JSON structure is malformed, Pydantic validation fails.

The system then records the analysis as failed instead of storing invalid clinical information.

This provides a safety boundary around the AI output.

19. Document Processing Failure Handling

Document-processing failures are also handled explicitly.

Possible failures include:

Empty text
Missing image
Unsupported image format
Corrupt image
Corrupt PDF
Unsupported PDF
No readable OCR text
OCR failure
PDF extraction failure

The backend converts these failures into clear API errors.

20. Backend and AI Separation

The application follows a layered architecture.

Frontend
    |
    v
FastAPI API
    |
    +----------------------+
    |                      |
    v                      v
Document Processing     AI Service
    |                      |
    +----------+-----------+
               |
               v
       Structured Report
               |
               v
          Pydantic
          Validation
               |
               v
           Database

The frontend never communicates directly with Gemini.

The Gemini API key is therefore kept on the backend.

This also allows the backend to control:

Validation
Error handling
Prompt construction
Structured output
Persistence
AI service failures
21. Database Persistence

The application currently uses SQLite for local development.

The database model stores:

Analysis
|
+-- id
+-- source_type
+-- filename
+-- status
+-- summary
+-- report_json
+-- extracted_text
+-- error_message
+-- created_at

The database stores both successful and failed analyses.

This allows the application to maintain an analysis history.

22. Successful Analysis Flow

A successful analysis follows this flow:

User Input
    |
    v
FastAPI
    |
    v
Create Processing Record
    |
    v
Document Processing
    |
    v
Extracted Text
    |
    v
Gemini AI
    |
    v
Structured JSON
    |
    v
Pydantic Validation
    |
    v
Save Completed Analysis
    |
    v
Return Report
    |
    v
Frontend

The analysis status changes from:

processing

to:

completed

when the report is successfully generated and stored.

23. Failed Analysis Flow

When processing or AI analysis fails, the failure is persisted.

User Input
    |
    v
Create Processing Record
    |
    v
Processing / AI
    |
    X
Failure
    |
    v
Save Failed Analysis
    |
    v
Store Error Message
    |
    v
Return API Error
    |
    v
Frontend Error Message

The analysis status becomes:

failed

The database also stores an error message where available.

This allows failed analyses to appear in the history rather than disappearing completely.

24. Final Report Generation

The frontend does not display raw Gemini JSON.

Instead, the backend returns the validated structured report.

The frontend presents the information in readable sections.

The report contains:

Clinical Review Report

Report Summary

Primary Concerns

Patient Information

Symptoms

Diagnoses / Conditions

Medications

Vitals

Allergies

Observations

Concerns

Missing / Incomplete Information

Inconsistencies

Review Items

This makes the generated information easier for a nontechnical user to understand.

25. Previous Report Retrieval

Completed and failed analyses are stored in the database.

The frontend can retrieve previous analyses using:

GET /api/analyze/history

An individual analysis can be opened using:

GET /api/analyze/history/{analysis_id}

The history response contains information such as:

Analysis ID
Source type
Filename
Status
Summary
Creation timestamp
Error message where applicable

This allows users to reopen previous reports.

26. AI/ML Testing Strategy

The backend contains automated tests covering the main AI and document-processing components.

Testing includes:

Document Processing

Tests verify:

Valid text processing
Empty text rejection
Text normalization
OCR

Tests verify:

Valid image processing
Missing image handling
Unsupported image handling
PDF Processing

Tests verify:

Normal PDF extraction
Missing PDF handling
Unsupported file handling
AI Service

Tests verify:

Empty input rejection
Valid structured report
Invalid structured output
Gemini service failure
Analysis API

Tests verify:

Successful text analysis
Image analysis
PDF analysis
Persistence
History retrieval
Individual report retrieval
Failed analysis persistence
Unsupported formats
Processing failures
Error handling

The backend currently contains:

29 automated tests
27. Reliability Strategy

The application treats document processing and AI analysis as failure-prone external operations.

The reliability strategy includes:

Input validation
File type validation
Document processing error handling
OCR error handling
AI API error handling
Structured response validation
Database persistence
Failure persistence
Clear frontend error messages
Automated backend testing

This prevents many common failures from being silently ignored.

28. Design Decisions
FastAPI

FastAPI was selected because it provides:

Python-based backend development
Pydantic integration
API routing
File upload support
Good support for structured request and response models
Simple local development
Gemini

Gemini is used as the AI service for clinical information extraction and structured report generation.

The model is accessed from the backend rather than the frontend.

Pydantic

Pydantic is used to define and validate the clinical report schema.

This provides predictable structured data between the AI service, backend, database, and frontend.

Tesseract OCR

Tesseract is used for extracting text from clinical images and scanned PDF pages.

It provides a local OCR pipeline without requiring a separate cloud OCR service.

PyMuPDF

PyMuPDF is used for rendering PDF pages when normal text extraction is unavailable and OCR processing is required.

SQLite

SQLite is used during local development because it is lightweight and does not require a separate database server.

The application architecture can be extended to PostgreSQL for production deployment.

29. Current Limitations

The current implementation has several limitations.

OCR Accuracy

OCR accuracy depends on the quality of the source image or scanned document.

Poor-quality documents may produce incomplete or incorrect extracted text.

Handwriting

Handwritten clinical documents may not produce reliable OCR output.

The system therefore surfaces cases where no readable text is detected.

AI Dependency

The report-generation stage depends on the availability of the Gemini API.

API errors, quotas, rate limits, or network failures can prevent analysis.

Source Quality

The quality of the generated report depends on the quality and completeness of the source document.

Missing source information cannot reliably be reconstructed by the system.

Local Database

The current development configuration uses SQLite.

A production deployment can use PostgreSQL or another managed relational database.

Clinical Use

The system is designed as a clinical document review and information-extraction tool.

It should not be treated as an autonomous diagnostic system.

Clinical decisions should be made by appropriately qualified professionals using the original source information and other relevant clinical context.

30. Future Improvements

Potential improvements include:

Improved medical OCR
Better handwriting recognition
Confidence scores for extracted fields
Document-quality scoring
Medical terminology normalization
Multiple-model validation
Human-in-the-loop review
PostgreSQL production database
Authentication
Authorization
Audit logging
Production monitoring
Observability
Improved document classification
Additional document formats
Containerized deployment
More extensive clinical document datasets using synthetic data
More advanced structured report validation
Automated monitoring of AI service failures
31. Security and Privacy Considerations

Clinical documents can contain sensitive information.

For development and demonstration, the application should use synthetic clinical data.

The Gemini API key is stored in the backend environment configuration rather than the frontend.

The frontend does not contain the Gemini API key.

The .env file is excluded from Git through .gitignore.

Uploaded files and local database files should also remain excluded from source control.

For production deployment, additional security controls should be implemented, including:

Authentication
Authorization
HTTPS
Secure secret management
Access logging
Audit trails
Data retention policies
Encryption
Secure database configuration
32. End-to-End AI Workflow

The complete AI workflow is:

1. User provides clinical document
              |
              v
2. FastAPI receives request
              |
              v
3. Input is validated
              |
              v
4. Document processor identifies usable text
              |
              v
5. OCR is used when required
              |
              v
6. Extracted text is normalized
              |
              v
7. Gemini receives source-grounded extraction prompt
              |
              v
8. Gemini returns structured JSON
              |
              v
9. Pydantic validates JSON
              |
              v
10. Medication entries are normalized
              |
              v
11. Clinical report is stored
              |
              v
12. Frontend receives structured report
              |
              v
13. Report is displayed in readable sections
              |
              v
14. Analysis remains available in history
33. Summary

The AI Clinical Document Reviewer uses a layered AI/ML pipeline to transform clinical documents into structured clinical review reports.

The main design principles are:

Support multiple document types
Convert documents into usable text
Use OCR for images and scanned PDFs
Keep AI processing on the backend
Use source-grounded extraction
Avoid unsupported clinical inference
Generate structured AI output
Validate AI output using Pydantic
Explicitly identify missing information
Surface concerns and review items
Persist successful and failed analyses
Provide readable frontend reports
Test both successful and failure workflows

The resulting architecture separates document processing, AI analysis, validation, persistence, and presentation into independent components, making the application easier to maintain and extend.