import pytesseract
from PIL import Image
import fitz
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        pass

    def extrair_texto_imagem(self, imagem_bytes: bytes) -> Optional[str]:
        try:
            imagem = Image.open(io.BytesIO(imagem_bytes))

            if imagem.mode != 'RGB':
                imagem = imagem.convert('RGB')

            texto = pytesseract.image_to_string(imagem, lang='por')

            texto = '\n'.join(line.strip() for line in texto.split('\n') if line.strip())

            logger.info(f"✅ Texto extraído da imagem: {len(texto)} caracteres")
            return texto

        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto da imagem: {e}")
            return None

    def extrair_texto_pdf(self, pdf_bytes: bytes) -> Optional[str]:
        try:
            documento = fitz.open(stream=pdf_bytes, filetype="pdf")
            texto_completo = []

            for num_pagina in range(len(documento)):
                pagina = documento[num_pagina]

                texto = pagina.get_text()

                if not texto.strip():
                    logger.info(f"Página {num_pagina + 1} sem texto nativo, usando OCR...")

                    pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom para melhor qualidade
                    imagem_bytes = pix.tobytes("png")

                    texto = self.extrair_texto_imagem(imagem_bytes)

                if texto:
                    texto_completo.append(texto.strip())

            documento.close()

            resultado = '\n\n'.join(texto_completo)
            logger.info(f"✅ Texto extraído do PDF: {len(resultado)} caracteres")
            return resultado

        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto do PDF: {e}")
            return None

    def processar_arquivo(self, arquivo_bytes: bytes, tipo_mime: str) -> Optional[str]:
        if tipo_mime.startswith('image/'):
            return self.extrair_texto_imagem(arquivo_bytes)
        elif tipo_mime == 'application/pdf':
            return self.extrair_texto_pdf(arquivo_bytes)
        else:
            logger.warning(f"⚠️ Tipo de arquivo não suportado: {tipo_mime}")
            return None