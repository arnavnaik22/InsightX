import PyPDF2
import io

def extract_text_from_pdf(file_stream) -> str:
    """
    Extracts complete text from an uploaded PDF file stream.
    Returns empty string if unreadable.
    """
    try:
        # Ensure compatibility with Django UploadedFile object by buffering directly
        if hasattr(file_stream, 'read'):
            content = file_stream.read()
        else:
            content = file_stream

        pdf_file = io.BytesIO(content) if isinstance(content, bytes) else file_stream
        reader = PyPDF2.PdfReader(pdf_file)
        
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text() or '')
        return " ".join(text_parts).strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
