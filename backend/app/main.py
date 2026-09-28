from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.database import Base, engine
from backend.app.api.routes.analysis import router as analysis_router
from backend.app.models.analysis import Analysis

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Clinical Document Reviewer",
    description="AI-powered clinical document analysis system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-clinical-document-reviewer-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "message": "AI Clinical Document Reviewer API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }