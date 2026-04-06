from reportlab.pdfgen import canvas
import PyPDF2
import io

print("Creating dummy PDF...")
buffer = io.BytesIO()
p = canvas.Canvas(buffer)
p.drawString(100, 100, "Hello World")
p.showPage()
p.save()
buffer.seek(0)
print("Dummy PDF created")

try:
    print("Reading PDF...")
    reader = PyPDF2.PdfReader(buffer)
    print("Pages:", len(reader.pages))
    print("Extracted:", reader.pages[0].extract_text())
except Exception as e:
    print("PyPDF2 error:", e)

