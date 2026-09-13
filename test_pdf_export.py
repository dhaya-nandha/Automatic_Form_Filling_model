import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from automation.pdf_filler import PDFFillerEngine

def test_pdf_export_pipeline():
    print("Testing Dual Upload (CV + Form) -> PDF Export Engine...")

    sample_cv = BASE_DIR / "sample_resume.txt"
    sample_form = BASE_DIR / "sample_form.html"

    assert sample_cv.exists(), "Sample CV missing"
    assert sample_form.exists(), "Sample Form missing"

    engine = PDFFillerEngine()
    output_pdf, summary = engine.process_and_export_pdf(str(sample_cv), str(sample_form))

    assert Path(output_pdf).exists(), f"PDF Output missing at {output_pdf}"
    assert Path(output_pdf).stat().st_size > 0, "PDF Output is empty (0 bytes)"

    print(f"  [SUCCESS] Generated filled PDF file at: {output_pdf}")
    print(f"  [SUCCESS] Filled {summary['filled_count']}/{summary['total_fields']} fields.")

if __name__ == "__main__":
    test_pdf_export_pipeline()
