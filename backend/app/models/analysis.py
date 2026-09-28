from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    source_type = Column(String(50), nullable=False)

    filename = Column(String(255), nullable=True)

    status = Column(String(50), nullable=False, default="processing")

    summary = Column(Text, nullable=True)

    report_json = Column(Text, nullable=True)

    extracted_text = Column(Text, nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )