import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from core.ingestion import DocumentIngestionEngine
from core.extractor import DocumentExtractorEngine
from automation.playwright_filler import PlaywrightFormFiller
from backend.database import SessionLocal, Base, engine
from backend.models import UserProfileField

def test_google_form_live_autofill():
    print("Testing Live Google Form Auto-Fill Pipeline...")

    # 1. Parse Jacinth Resume.pdf
    cv_path = BASE_DIR / "uploads" / "cv_Jacinth Resume.pdf"
    text, _ = DocumentIngestionEngine.extract_text(str(cv_path))

    extractor = DocumentExtractorEngine()
    extracted = extractor.extract_structured_profile(text, source_doc=cv_path.name)

    print("\n[EXTRACTED PROFILE FROM CV]:")
    user_profile = {}
    for k, v in extracted.items():
        print(f"  - {k:<25}: {v['value']}")
        user_profile[k] = {"value": v["value"], "confidence": v["confidence"], "source": v["source"]}

    # 2. Run Playwright Auto-fill on live Google Form URL
    gform_url = "https://docs.google.com/forms/d/e/1FAIpQLSeuoP6EKvaRjYLa0rWlGFlsZpOwKJNVufoNg4oy7o5sdnswMw/viewform"
    filler = PlaywrightFormFiller(headless=True)
    summary = filler.fill_form(gform_url, user_profile)

    print("\n[FILL SUMMARY]:")
    print(f"  Status       : {summary['status']}")
    print(f"  Total Fields : {summary['total_fields']}")
    print(f"  Filled Count : {summary['filled_count']}")
    print(f"  Flagged Count: {summary['flagged_count']}")

    print("\n[MATCH DETAILS]:")
    for m in summary["match_details"]:
        print(f"  Label: '{m['label']:<30}' -> Canonical: {str(m['matched_canonical_key']):<20} | Value: {str(m['derived_value']):<30} | Action: {m['action']}")

if __name__ == "__main__":
    test_google_form_live_autofill()
