from django.shortcuts import render
from django.http import JsonResponse

from .models import FileUpload
from .forms import FileUploadForm
import pandas as pd
from docx import Document
import mimetypes

from parser.parsers import *


# Create your views here.

HEADER_MAP = {
    "transaction_date": ["Date", "Дата", "Дата операции", "Дата проводки"],
    "description": [
        "Description",
        "Описание",
        "Назначение платежа",
        "Детали",
        "Контрагент",
    ],
    "amount": ["Amount", "Сумма"],
    "debit": ["Debit", "Расход", "Списание", "Дебет"],
    "credit": ["Credit", "Приход", "Поступление", "Кредит"],
    "currency": ["Currency", "Валюта"],
    "KNP": ["КНП", "Код назначения платежа"],
    "BIN": ["БИН/ИИН", "БИН", "Контрагент ИИН/БИН"],
    "IIN": ["ИИН", "Контрагент ИИН/БИН"],
}


def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.save()
            file = upload_file.file
            name = file.name

            try:
                if name.endswith(".csv"):
                    df = read_csv_with_encoding(file)
                    df = map_columns(df, HEADER_MAP)
                    df = coerce_types(df)
                    return JsonResponse(
                        {"extracted_tables": df.to_dict(orient="records")}
                    )

                elif name.endswith(".xlsx"):
                    df = pd.read_excel(file)
                    df = map_columns(df, HEADER_MAP)
                    df = coerce_types(df)
                    return JsonResponse(
                        {"extracted_tables": df.to_dict(orient="records")}
                    )

                elif name.endswith(".docx"):
                    content = file.read()
                    docx_data = parse_docx(content)

                    text_df = pd.DataFrame([{"text": docx_data["extracted_text"]}])

                    table_dfs = [
                        map_columns(pd.DataFrame(t[1:], columns=t[0]), HEADER_MAP)
                        for t in docx_data["extracted_tables"]
                        if len(t) > 1
                    ]
                    table_dfs = [coerce_types(df) for df in table_dfs]

                    return JsonResponse(
                        {
                            "extracted_text": text_df.to_dict(orient="records"),
                            "extracted_tables": [
                                df.to_dict(orient="records") for df in table_dfs
                            ],
                        }
                    )

                elif name.endswith(".pdf"):
                    df = parse_pdf(file.read())
                    if df.empty:  
                        file.seek(0)  
                        images = pdf_to_images(file.read())
                        ocr_texts = []
                        for image_bytes in images:
                            text = detect_text(image_bytes)
                            ocr_texts.append(text)
                        full_text = "\n\n".join(ocr_texts)
                        return JsonResponse({"extracted_text": ocr_texts})
                    else:
                        return JsonResponse(
                            {"extracted_text": df.to_dict(orient="records")}
                        )

                elif name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
                    ocr_result = detect_text(file.read())
                    return JsonResponse({"extracted_text": ocr_result})

                else:
                    return JsonResponse({"error": "Unsupported file format"})

            except Exception as e:
                return JsonResponse({"error": str(e)})

    else:
        form = FileUploadForm()

    return render(request, "parser/upload.html", {"form": form})
