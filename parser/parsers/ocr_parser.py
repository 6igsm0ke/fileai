import os
import fitz
from google.cloud import vision
import re
import io

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vision-key.json'
WORD = re.compile(r'\w+')

def detect_text(file_content):
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=file_content)

    response = client.document_text_detection(image=image)
    texts = response.text_annotations

    ocr_text = texts[0].description if texts else ""

    if response.error.message:
        raise Exception(
            f"{response.error.message}\nSee: https://cloud.google.com/apis/design/errors"
        )
    return ocr_text


def pdf_to_images(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        image_bytes = pix.tobytes("png")
        images.append(image_bytes)
    doc.close()
    return images