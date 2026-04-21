import docx
import os
from pypdf import PdfReader

def get_text_from_docx(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

def get_text_from_pdf(filename):
    reader = PdfReader(filename)
    fullText = []
    for page in reader.pages:
        fullText.append(page.extract_text())
    return '\n'.join(fullText)

def get_text(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.docx':
        return get_text_from_docx(filename)
    elif ext == '.pdf':
        return get_text_from_pdf(filename)
    else:
        return f"Unsupported file type: {ext}"

resume_path = r'C:\Users\SUSHMA\Downloads\ShiyasRasi_AutomationManualTestEngineer.pdf'
jd_path = r'C:\Users\SUSHMA\Downloads\JobDescription.docx'

print("--- RESUME ---")
try:
    print(get_text(resume_path))
except Exception as e:
    print(f"Error reading resume: {e}")

print("\n--- JD ---")
try:
    print(get_text(jd_path))
except Exception as e:
    print(f"Error reading JD: {e}")
