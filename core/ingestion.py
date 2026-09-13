import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple

class DocumentIngestionEngine:
    """Multi-format Document Ingestion Engine (PDF, DOCX, TXT, Images)"""

    @staticmethod
    def extract_text(file_path: str) -> Tuple[str, str]:
        """
        Extract raw text from specified file path.
        Returns (extracted_text, file_type)
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()

        if ext == ".txt":
            return DocumentIngestionEngine._read_txt(path), "txt"
        elif ext == ".docx":
            return DocumentIngestionEngine._read_docx(path), "docx"
        elif ext == ".pdf":
            return DocumentIngestionEngine._read_pdf(path), "pdf"
        elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            return DocumentIngestionEngine._read_image(path), "image"
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _read_txt(path: Path) -> str:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def _read_docx(path: Path) -> str:
        try:
            import docx
            doc = docx.Document(path)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except ImportError:
            # Fallback to direct XML parsing if python-docx is unavailable
            with zipfile.ZipFile(path) as z:
                xml_content = z.read("word/document.xml")
            root = ET.fromstring(xml_content)
            paragraphs = []
            for p in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                texts = [node.text for node in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)

    @staticmethod
    def _read_pdf(path: Path) -> str:
        text_content = []
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_content.append(t)
        except Exception:
            pass

        if not text_content:
            try:
                import pdfplumber
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text_content.append(t)
            except Exception:
                pass

        return "\n".join(text_content) if text_content else "PDF content could not be read as text."

    @staticmethod
    def _read_image(path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(str(path))
            return pytesseract.image_to_string(img)
        except Exception as e:
            return f"[OCR Required] OCR execution unavailable: {str(e)}. Install Tesseract-OCR for image support."
