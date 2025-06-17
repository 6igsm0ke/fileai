from django.shortcuts import render
from django.http import JsonResponse

from .models import FileUpload
from .forms import FileUploadForm
import pandas as pd
from docx import Document
import fitz
import io


# Create your views here.
def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.save()
            file = upload_file.file

            name = file.name

            try:
                if name.endswith(".csv"):
                    df = pd.read_csv(file)
                elif name.endswith(".xlsx"):
                    df = pd.read_excel(file)
                elif name.endswith(".docx"):
                    df = parse_docx(file.read())
                elif name.endswith(".pdf"):
                    df = parse_pdf(file.read())
                else:
                    return JsonResponse({"error": "Unsupported file format"})

                return JsonResponse({"data": df.to_dict(orient="records")})
            except Exception as e:
                return JsonResponse({"error": str(e)})
    else:
        form = FileUploadForm()

    return render(request, "parser/upload.html", {"form": form})


def parse_docx(content):
    doc = Document(io.BytesIO(content))
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    return pd.DataFrame([{"text": line} for line in lines])


def parse_pdf(content):
    pdf = fitz.open(stream=content, filetype="pdf")
    lines = []
    for page in pdf:
        lines.extend(page.get_text("text").split("\n"))
    pdf.close()
    return pd.DataFrame([{"text": line} for line in lines if line.strip()])
