import fitz
from typing import Optional
from src.logger import setup_logger

logger = setup_logger(__name__)

def pdf_to_image_dict(pdf_path: str) -> Optional[dict]:
    image_dict = {}
    try:
        pdf_document = fitz.open(pdf_path)
        logger.info(f"Loaded the pdf document {pdf_path} with {len(pdf_document)} pages.")
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pixmap = page.get_pixmap()
            image_dict[page_number] = pixmap.tobytes("png")
            logger.info(f"Processed page {page_number} successfully")
        pdf_document.close()
        return image_dict
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return None
