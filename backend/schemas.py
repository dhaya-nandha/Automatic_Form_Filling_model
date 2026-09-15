from typing import List, Dict, Optional, Any
from datetime import datetime

try:
    from pydantic import BaseModel
except Exception as e:
    print(f"[Schemas Warning] Pydantic C-extension fallback active: {e}")
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return self.__dict__
        def dict(self):
            return self.__dict__

class ProfileFieldBase(BaseModel):
    canonical_key: str
    field_value: str
    confidence_score: float = 1.0
    source_document: Optional[str] = None

class ProfileFieldCreate(ProfileFieldBase):
    pass

class ProfileFieldResponse(ProfileFieldBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    extracted_fields: Dict[str, str]
    message: str

class DetectedFormField(BaseModel):
    field_id: str
    label: str
    field_type: str = "text" # text, select, checkbox, radio, date
    options: Optional[List[str]] = None
    selector: Optional[str] = None

class MatchResultItem(BaseModel):
    field_id: str
    label: str
    matched_canonical_key: Optional[str] = None
    derived_value: Optional[str] = None
    similarity_score: float = 0.0
    action: str # "AUTO_FILL", "INFERRED", "NEEDS_REVIEW"
    source_document: Optional[str] = None

class FormMatchRequest(BaseModel):
    target_form: str
    fields: List[DetectedFormField]

class FormMatchResponse(BaseModel):
    target_form: str
    matches: List[MatchResultItem]
    auto_fill_count: int
    review_needed_count: int

class FormFillExecuteRequest(BaseModel):
    form_url_or_path: str
    user_overrides: Optional[Dict[str, str]] = None  # Handled manual review inputs
