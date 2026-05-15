import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import fitz
import io
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = 1600
MIN_IMAGE_DIMENSION = 1000
PSM_FALLBACK_ORDER = [6, 4, 11]
TESSERACT_BASE_CONFIG = "--oem 3 -l por+eng"
PDF_OCR_MATRIX = fitz.Matrix(3, 3)


class OCRService:
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        image = image.convert('L')
        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)
        return image

    def _resize_image(self, image: Image.Image) -> Image.Image:
        w, h = image.size
        largest = max(w, h)

        if largest > MAX_IMAGE_DIMENSION:
            scale = MAX_IMAGE_DIMENSION / largest
            new_size = (int(w * scale), int(h * scale))
            image = image.resize(new_size, Image.LANCZOS)
            logger.info(f"Imagem reduzida de {w}x{h} para {image.size}")
        elif largest < MIN_IMAGE_DIMENSION:
            scale = MIN_IMAGE_DIMENSION / largest
            new_size = (int(w * scale), int(h * scale))
            image = image.resize(new_size, Image.LANCZOS)
            logger.info(f"Imagem ampliada de {w}x{h} para {image.size}")

        return image

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[|]{2,}|_{3,}', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        return text

    def _extract_with_fallback(self, image: Image.Image) -> str:
        for psm in PSM_FALLBACK_ORDER:
            config = f"{TESSERACT_BASE_CONFIG} --psm {psm}"
            text = pytesseract.image_to_string(image, config=config)
            text = self._clean_text(text)
            if len(text) > 20:
                logger.info(f"OCR bem-sucedido com psm={psm} ({len(text)} caracteres)")
                return text
        return text

    def extract_text_from_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = self._resize_image(image)
            image = self._preprocess_image(image)

            text = self._extract_with_fallback(image)

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
                    pix = page.get_pixmap(matrix=PDF_OCR_MATRIX)
                    image_bytes = pix.tobytes("png")
                    text = self.extract_text_from_image(image_bytes)

                if text:
                    full_text.append(self._clean_text(text) if isinstance(text, str) else text)

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
            logger.warning(f"Tipo de arquivo não suportado: {mime_type}")
            return None
