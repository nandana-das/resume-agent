import pdfplumber, docx, io

def extract_resume_text(uploaded_file) -> str:
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(
                p.extract_text() for p in pdf.pages if p.extract_text()
            ).strip()
    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        return "\n".join(
            p.text for p in doc.paragraphs if p.text.strip()
        ).strip()