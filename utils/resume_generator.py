import io
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generate_resume_docx(resume_text: str) -> bytes:
    doc = Document()
    # Set narrow margins for resume
    for section in doc.sections:
        section.top_margin = Pt(36)
        section.left_margin = Pt(54)
        section.right_margin = Pt(54)
    # Parse lines and format headings, bullets, body text
    # Returns bytes for st.download_button()
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read()