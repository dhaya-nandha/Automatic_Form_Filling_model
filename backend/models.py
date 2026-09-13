from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class DocumentRecord(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String)
    extracted_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class UserProfileField(Base):
    __tablename__ = "user_profile_fields"

    id = Column(Integer, primary_key=True, index=True)
    canonical_key = Column(String, index=True, nullable=False)  # e.g., 'full_name', 'email'
    field_value = Column(Text, nullable=False)
    confidence_score = Column(Float, default=1.0)
    source_document = Column(String, nullable=True)             # Provenance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FormFillSession(Base):
    __tablename__ = "form_sessions"

    id = Column(Integer, primary_key=True, index=True)
    form_target = Column(String, nullable=False)               # URL or PDF filename
    status = Column(String, default="PENDING")                 # PENDING, IN_PROGRESS, REVIEW_NEEDED, COMPLETED
    fields_detected = Column(JSON, nullable=True)              # Raw detected form fields
    matching_results = Column(JSON, nullable=True)             # Auto-filled vs flagged mapping
    created_at = Column(DateTime, default=datetime.utcnow)
