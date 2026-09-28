from typing import List, Optional

from pydantic import BaseModel, Field


class PatientInfo(BaseModel):
    name: Optional[str]
    age: Optional[str]
    gender: Optional[str]
    date: Optional[str]


class Symptom(BaseModel):
    name: str
    details: Optional[str] = None


class Diagnosis(BaseModel):
    condition: str
    details: Optional[str] = None


class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    details: Optional[str] = None


class Vital(BaseModel):
    name: str
    value: Optional[str] = None
    unit: Optional[str] = None


class Observation(BaseModel):
    observation: str
    details: Optional[str] = None


class Concern(BaseModel):
    concern: str
    details: Optional[str] = None


class MissingInformation(BaseModel):
    field: str
    details: Optional[str] = None


class Inconsistency(BaseModel):
    issue: str
    details: Optional[str] = None


class ReviewItem(BaseModel):
    item: str
    details: Optional[str] = None


class ClinicalReport(BaseModel):
    report_summary: str = Field(
        description="Concise summary of the clinical document."
    )

    primary_concerns: List[str]

    patient_info: PatientInfo

    symptoms: List[Symptom]

    diagnoses: List[Diagnosis]

    medications: List[Medication]

    vitals: List[Vital]

    allergies: List[str]

    observations: List[Observation]

    concerns: List[Concern]

    missing_information: List[MissingInformation]

    inconsistencies: List[Inconsistency]

    review_items: List[ReviewItem]