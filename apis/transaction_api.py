from typing import Dict, Any
from apis.base_api import BaseAPI
import logging

logger = logging.getLogger(__name__)


class TransactionAPI(BaseAPI):

    async def create_transaction(
            self,
            telegram_id: str,
            original_message: str
    ) -> Dict[str, Any]:
        data = {
            "telegram_id": telegram_id,
            "original_message": original_message
        }

        result = await self._request("POST", "/transactions", data)

        logger.debug(f"Resultado da API: {result}")

        if result['success']:
            transaction = result['data'].get('transaction', {})
            category = transaction.get('category', {})

            return {
                'success': True,
                'data': {
                    'transaction_id': transaction.get('id'),
                    'type': transaction.get('type'),
                    'category': category.get('title', 'desconhecido'),
                    'amount': float(transaction.get('amount', 0)),
                    'description': transaction.get('description', '')
                }
            }

        return result