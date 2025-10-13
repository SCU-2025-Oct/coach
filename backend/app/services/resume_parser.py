from typing import Tuple
import mimetypes
import fitz  # PyMuPDF
from docx import Document

def sniff_mime(path: str) -> str:
    mt, _ = mimetypes.guess_type(path)
    return mt or "application/octet-stream"

def extract_text(path: str) -> Tuple[str, str]:
    mime = sniff_mime(path)
    if mime == "application/pdf":
        doc = fitz.open(path)
        text = []
        for page in doc:
            text.append(page.get_text("text"))
        return ("\n".join(text).strip(), mime)
    if mime in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"):
        d = Document(path)
        text = "\n".join(p.text for p in d.paragraphs)
        return (text.strip(), mime)
    raise ValueError(f"Unsupported file type: {mime}")
