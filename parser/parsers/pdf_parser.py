import fitz
import pandas as pd

def parse_pdf(content):
    pdf = fitz.open(stream=content, filetype="pdf")
    lines = []
    for page in pdf:
        lines.extend(page.get_text("text").split("\n"))
    pdf.close()
    return pd.DataFrame([{"text": line} for line in lines if line.strip()])
