import logging
from typing import BinaryIO

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def extract_text_from_pdf(pdf_bytes_io: BinaryIO) -> str:
    """간단한 PDF 텍스트 추출기.

    우선 PyPDF2 시도 → 실패 시 빈 문자열 반환.
    실패하거나 텍스트가 거의 없으면 pytesseract로 OCR 시도

    """
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(pdf_bytes_io)
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception as e:
                logging.warning(f"페이지 추출 실패: {e}")
                continue
        text_result = "\n".join(t.strip() for t in texts if t)
        if text_result.strip():
            return text_result

    except Exception as e:
        logging.error("PyPDF2 처리 실패", exc_info=True)
        return ""

    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        pdf_bytes_io.seek(0)
        images = convert_from_bytes(pdf_bytes_io.read())
        texts = []
        for img in images:
            text = pytesseract.image_to_string(img, lang="kor+eng")
            if text.strip():
                texts.append(text.strip())

        return "\n".join(texts)
    except Exception as e:
        logging.error("OCR 처리 실패", exc_info=True)
        return ""
