import easyocr
from PIL import Image
import fitz
import io
from typing import Optional
import logging
import numpy as np

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.reader = easyocr.Reader(['pt', 'en'], gpu=False)
        logger.info("EasyOCR inicializado")
    
    def extract_text_from_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')

            image_np = np.array(image)

            results = self.reader.readtext(image_np)

            text = '\n'.join([result[1] for result in results])
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

            logger.info(f"Texto extraído da imagem: {len(text)} caracteres")
            return text
        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto da imagem: {e}")
            return None

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> Optional[str]:
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = []

            for page_num in range(len(document)):
                page = document[page_num]
                text = page.get_text()

                if not text.strip():
                    logger.info(f"Página {page_num + 1} sem texto nativo, usando OCR...")
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    image_bytes = pix.tobytes("png")
                    text = self.extract_text_from_image(image_bytes)

                if text:
                    full_text.append(text.strip())

            document.close()
            result = '\n\n'.join(full_text)
            logger.info(f"Texto extraído do PDF: {len(result)} caracteres")
            return result
        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto do PDF: {e}")
            return None

    def process_file(self, file_bytes: bytes, mime_type: str) -> Optional[str]:
        if mime_type.startswith('image/'):
            return self.extract_text_from_image(file_bytes)
        elif mime_type == 'application/pdf':
            return self.extract_text_from_pdf(file_bytes)
        else:
            logger.warning(f"⚠️ Tipo de arquivo não suportado: {mime_type}")
            return None