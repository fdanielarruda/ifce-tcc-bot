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
                    'description': transaction.get('description', '-------'),
                    'balance': float(transaction.get('balance', 0))
                }
            }

        return result

    async def get_summary(
            self,
            telegram_id: str,
            summary_type: str
    ) -> Dict[str, Any]:
        endpoint = f"/transactions/summary/{summary_type}?telegram_id={telegram_id}"
        result = await self._request("GET", endpoint)

        if result['success']:
            return {
                'success': True,
                'data': result['data'].get('summary', [])
            }

        return result

    async def get_recent_transactions(
            self,
            telegram_id: str,
            limit: int = 5
    ) -> Dict[str, Any]:
        endpoint = f"/transactions?telegram_id={telegram_id}&limit={limit}"
        result = await self._request("GET", endpoint)

        if result['success']:
            transactions = result['data'].get('transactions', result['data'])
            if isinstance(transactions, list):
                return {'success': True, 'data': transactions}
            return {'success': True, 'data': []}

        return result

    async def update_transaction(
            self,
            transaction_id: str,
            telegram_id: str,
            amount: float = None,
            description: str = None
    ) -> Dict[str, Any]:
        data = {"telegram_id": telegram_id}
        if amount is not None:
            data["amount"] = amount
        if description is not None:
            data["description"] = description

        result = await self._request("PUT", f"/transactions/{transaction_id}", data)

        if result['success']:
            transaction = result['data'].get('transaction', result['data'])
            return {'success': True, 'data': transaction}

        return result
