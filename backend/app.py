import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
import shutil
import os
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config
from backend.database import engine, get_db, Base
from backend.models import UserProfileField, DocumentRecord, FormFillSession
from backend.schemas import (
    DocumentUploadResponse, ProfileFieldResponse,
    FormMatchRequest, FormMatchResponse, FormFillExecuteRequest
)
from core.ingestion import DocumentIngestionEngine
from core.extractor import DocumentExtractorEngine
from core.field_matcher import SemanticFieldMatcher
from automation.playwright_filler import PlaywrightFormFiller
from automation.pdf_filler import PDFFillerEngine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automatic Form-Filling Tool API & Mobile App",
    description="Backend API & Mobile App for Document Ingestion, Entity NER, Semantic Field Matching, and Automated Form Filling",
    version="1.0.0"
)

# Enable CORS for browser extension, Android APK, and mobile devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

extractor = DocumentExtractorEngine()
matcher = SemanticFieldMatcher()
filler = PlaywrightFormFiller(headless=True)
pdf_engine = PDFFillerEngine()

# Mount Mobile App static directory
mobile_dir = Path(config.BASE_DIR) / "mobile_app"
if mobile_dir.exists():
    app.mount("/mobile", StaticFiles(directory=str(mobile_dir), html=True), name="mobile")

# Ensure downloads directory exists
downloads_dir = Path(config.BASE_DIR) / "downloads"
downloads_dir.mkdir(exist_ok=True)

def get_latest_user_profile(db: Session) -> Dict[str, Dict[str, Any]]:
    """Helper to build user profile dict where newest uploaded document facts take top priority."""
    db_fields = db.query(UserProfileField).order_by(UserProfileField.id.asc()).all()
    user_profile = {}

    for f in db_fields:
        user_profile[f.canonical_key] = {
            "value": f.field_value,
            "confidence": f.confidence_score,
            "source": f.source_document
        }

    # If DB is empty, check for Jacinth Resume in uploads as fallback
    if not user_profile:
        fallback_cv = Path(config.BASE_DIR) / "uploads" / "cv_Jacinth Resume.pdf"
        if fallback_cv.exists():
            text, _ = DocumentIngestionEngine.extract_text(str(fallback_cv))
            ext = extractor.extract_structured_profile(text, source_doc=fallback_cv.name)
            for k, v in ext.items():
                user_profile[k] = {"value": v["value"], "confidence": v["confidence"], "source": v["source"]}

    return user_profile

@app.get("/")
def root():
    index_path = Path(config.BASE_DIR) / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return RedirectResponse(url="/mobile/")

@app.get("/style.css")
def get_style_css():
    css_path = Path(config.BASE_DIR) / "style.css"
    if css_path.exists():
        return FileResponse(str(css_path), media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")

@app.get("/app.js")
def get_app_js():
    js_path = Path(config.BASE_DIR) / "app.js"
    if js_path.exists():
        return FileResponse(str(js_path), media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JS not found")

@app.get("/preview-image")
def get_preview_image():
    img_path = Path(config.BASE_DIR) / "filled_form_preview.png"
    if img_path.exists():
        return FileResponse(str(img_path))
    raise HTTPException(status_code=404, detail="Preview image not found")

@app.get("/api/download-apk")
def download_apk():
    """Streams compiled Android APK file directly for device installation."""
    apk_paths = [
        Path(config.BASE_DIR) / "FormFill_AI.apk",
        Path(config.BASE_DIR) / "android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    ]
    for apk_path in apk_paths:
        if apk_path.exists():
            return FileResponse(
                path=str(apk_path),
                filename="FormFill_AI.apk",
                media_type="application/vnd.android.package-archive",
                headers={"Content-Length": str(os.path.getsize(apk_path))}
            )
    raise HTTPException(status_code=404, detail="APK build in progress or not found")

@app.get("/api/download-file/{filename}")
def download_file(filename: str):
    """Streams filled PDF file directly for browser download."""
    file_path = downloads_dir / filename
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            filename="filled_application_form.pdf",
            media_type="application/pdf",
            headers={"Content-Length": str(os.path.getsize(file_path))}
        )
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/fill-and-export-pdf")
def fill_and_export_pdf(
    cv_file: UploadFile = File(...),
    form_file: UploadFile = File(...)
):
    """
    Accepts CV/Resume + Application Form file, extracts facts from CV, fills Application Form, 
    and returns JSON with completed PDF download URL.
    """
    temp_dir = Path(config.BASE_DIR) / "uploads"
    temp_dir.mkdir(exist_ok=True)

    cv_path = temp_dir / f"cv_{cv_file.filename}"
    form_path = temp_dir / f"form_{form_file.filename}"

    with open(cv_path, "wb") as b1:
        shutil.copyfileobj(cv_file.file, b1)
    with open(form_path, "wb") as b2:
        shutil.copyfileobj(form_file.file, b2)

    try:
        output_pdf, summary = pdf_engine.process_and_export_pdf(str(cv_path), str(form_path))
        if Path(output_pdf).exists():
            pdf_filename = f"filled_application_{int(time.time())}.pdf"
            dest_path = downloads_dir / pdf_filename
            shutil.copyfile(output_pdf, dest_path)
            return {
                "status": "SUCCESS",
                "filename": pdf_filename,
                "download_url": f"/api/download-file/{pdf_filename}"
            }
        raise HTTPException(status_code=500, detail="PDF generation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process and export PDF: {str(e)}")

@app.post("/api/upload-document", response_model=DocumentUploadResponse)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads document (PDF, DOCX, TXT), parses content, extracts key profile attributes and updates Profile DB."""
    temp_dir = Path(config.BASE_DIR) / "uploads"
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / file.filename

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Ingest text
        text_content, file_type = DocumentIngestionEngine.extract_text(str(temp_file_path))

        # 2. Record Document
        doc_rec = DocumentRecord(filename=file.filename, file_type=file_type, extracted_text=text_content)
        db.add(doc_rec)
        db.commit()
        db.refresh(doc_rec)

        # 3. Extract entities
        extracted = extractor.extract_structured_profile(text_content, source_doc=file.filename)

        # 4. Upsert User Profile fields
        extracted_summary = {}
        for c_key, data in extracted.items():
            val = data["value"]
            conf = data["confidence"]
            extracted_summary[c_key] = val

            # Update existing key or insert new row
            existing = db.query(UserProfileField).filter(UserProfileField.canonical_key == c_key).first()
            if existing:
                existing.field_value = val
                existing.confidence_score = conf
                existing.source_document = file.filename
            else:
                db.add(UserProfileField(
                    canonical_key=c_key,
                    field_value=val,
                    confidence_score=conf,
                    source_document=file.filename
                ))
        db.commit()

        return {
            "document_id": doc_rec.id,
            "filename": file.filename,
            "extracted_fields": extracted_summary,
            "message": f"Successfully extracted {len(extracted)} profile fields."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/api/profile", response_model=List[ProfileFieldResponse])
def get_profile(db: Session = Depends(get_db)):
    """Retrieves all stored canonical profile key-value pairs."""
    return db.query(UserProfileField).all()

@app.post("/api/match-fields")
def match_fields(request: FormMatchRequest, db: Session = Depends(get_db)):
    """Accepts list of form inputs and returns predicted field matches & suggested auto-fill actions."""
    user_profile = get_latest_user_profile(db)
    raw_fields = [
        f.model_dump() if hasattr(f, "model_dump") else f.dict() if hasattr(f, "dict") else (f if isinstance(f, dict) else getattr(f, "__dict__", {}))
        for f in request.fields
    ]
    match_results = matcher.match_and_fill(raw_fields, user_profile)

    auto_fill_count = sum(1 for m in match_results if m["action"] in ["AUTO_FILL", "INFERRED"])
    review_needed_count = len(match_results) - auto_fill_count

    return {
        "target_form": request.target_form,
        "matches": match_results,
        "auto_fill_count": auto_fill_count,
        "review_needed_count": review_needed_count
    }

@app.post("/api/fill-form")
def fill_form_endpoint(req: FormFillExecuteRequest, db: Session = Depends(get_db)):
    """Triggers Playwright automated browser form filling."""
    user_profile = get_latest_user_profile(db)

    result = filler.fill_form(
        form_target=req.form_url_or_path,
        user_profile=user_profile,
        overrides=req.user_overrides
    )
    return result
