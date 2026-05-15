import easyocr
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import fitz
import io
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = 2400
MIN_IMAGE_DIMENSION = 1400
PDF_OCR_MATRIX = fitz.Matrix(3, 3)


class OCRService:
    def __init__(self):
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            self._reader = easyocr.Reader(['pt', 'en'], gpu=False)
        return self._reader

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        image = image.convert('L')
        image = image.filter(ImageFilter.MedianFilter(size=3))
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = ImageEnhance.Sharpness(image).enhance(1.5)
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

    def _extract_text(self, image: Image.Image) -> str:
        reader = self._get_reader()
        np_image = np.array(image)
        results = reader.readtext(np_image, paragraph=False, detail=1)

        if not results:
            return ''

        results.sort(key=lambda r: r[0][0][1])
        lines = []
        current_line = [results[0]]
        for r in results[1:]:
            y_current = r[0][0][1]
            y_prev = current_line[-1][0][0][1]
            if abs(y_current - y_prev) <= 10:
                current_line.append(r)
            else:
                current_line.sort(key=lambda x: x[0][0][0])
                lines.append(' '.join(item[1] for item in current_line))
                current_line = [r]
        current_line.sort(key=lambda x: x[0][0][0])
        lines.append(' '.join(item[1] for item in current_line))

        text = '\n'.join(lines)
        logger.info(f"EasyOCR extraiu {len(results)} blocos de texto")
        return text

    def extract_text_from_image(self, image_bytes: bytes) -> Optional[str]:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = self._resize_image(image)
            image = self._preprocess_image(image)

            text = self._clean_text(self._extract_text(image))

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
