from typing import Dict, Any
from apis.transaction_api import TransactionAPI
from services.ocr_service import OCRService
import logging

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self):
        self.transaction_api = TransactionAPI()
        self.ocr_service = OCRService()

    async def process_text_transaction(self, text: str, telegram_id: str) -> str:
        result = await self.transaction_api.create_transaction(
            telegram_id=telegram_id,
            original_message=text
        )

        if result['success']:
            return self._format_success_message(result['data'])

        return f"⚠️ {result['message']}"

    async def process_receipt(
            self,
            file_bytes: bytes,
            mime_type: str,
            telegram_id: str
    ) -> str:
        logger.info(f"📄 Processando comprovante do tipo: {mime_type}")

        extracted_text = self.ocr_service.process_file(file_bytes, mime_type)

        if not extracted_text:
            return (
                "❌ Não foi possível extrair texto do comprovante. "
                "Tente enviar uma imagem mais nítida ou digite manualmente."
            )

        if len(extracted_text) < 10:
            return (
                "⚠️ Pouco texto identificado no comprovante. "
                "Tente enviar uma imagem mais clara ou digite a transação manualmente."
            )

        logger.info(
            f"📝 Texto extraído ({len(extracted_text)} caracteres):\n"
            f"{extracted_text[:200]}..."
        )

        return await self.process_text_transaction(extracted_text, telegram_id)

    def _format_success_message(self, data: Dict[str, Any]) -> str:
        transaction_type = "Despesa" if data['type'] == "despesa" else "Receita"

        message = (
            f"✅ Transação registrada!\n"
            f"\n🆔 ID: {data['transaction_id']}"
            f"\n📂 Categoria: {data['category']}"
            f"\n💰 {transaction_type}: R$ {data['amount']:.2f}"
            f"\n📝 {data['description']}"
        )

        return message