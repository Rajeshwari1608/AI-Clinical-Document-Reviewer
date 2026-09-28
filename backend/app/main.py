from fastapi import FastAPI

from app.core.database import Base, engine
from app.models.analysis import Analysis

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Clinical Document Reviewer",
    description="AI-powered clinical document analysis system",
    version="1.0.0"
)


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