from pypdf import PdfReader

def extract_pdf_text(path: str) -> str:
    """
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {path}: {e}")
        return ""
