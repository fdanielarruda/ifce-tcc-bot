import pytesseract
from PIL import Image
import fitz
import io
from typing import Optional
import logging

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = 1600
TESSERACT_CONFIG = "--oem 3 --psm 6 -l por+eng"


class OCRService:
    def extract_text_from_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')

            w, h = image.size
            if max(w, h) > MAX_IMAGE_DIMENSION:
                scale = MAX_IMAGE_DIMENSION / max(w, h)
                image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
                logger.info(f"Imagem redimensionada de {w}x{h} para {image.size}")

            text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
            text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())

            logger.info(f"Texto extraído da imagem: {len(text)} caracteres")
            return text or None
        except Exception as e:
            logger.error(f"Erro ao extrair texto da imagem: {e}")
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
            return result or None
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            return None

    def process_file(self, file_bytes: bytes, mime_type: str) -> Optional[str]:
        if mime_type.startswith('image/'):
            return self.extract_text_from_image(file_bytes)
        elif mime_type == 'application/pdf':
            return self.extract_text_from_pdf(file_bytes)
        else:
            logger.warning(f"⚠️ Tipo de arquivo não suportado: {mime_type}")
            return None
