import re
from typing import Dict, Any
from apis.user_api import UserAPI
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.user_api = UserAPI()

    async def check_user_exists(self, telegram_id: str) -> bool:
        result = await self.user_api.check_user(filter_by='telegram_id', value=telegram_id)
        return result['success'] and bool(result.get('data', {}).get('users'))

    async def check_email_exists(self, email: str) -> bool:
        result = await self.user_api.check_user(filter_by='email', value=email)
        return result['success'] and bool(result.get('data', {}).get('users'))

    async def register_user(
            self,
            name: str,
            email: str,
            telegram_id: str
    ) -> Dict[str, Any]:
        if not self.validate_email(email):
            return {
                'success': False,
                'message': 'Email inválido'
            }

        result = await self.user_api.create_user(name, email, telegram_id)

        if result['success']:
            return {
                'success': True,
                'message': 'Usuário cadastrado com sucesso',
                'data': result.get('data')
            }

        logger.error(f"❌ Erro ao cadastrar usuário: {result.get('message')}")
        return result

    async def delete_user(
            self,
            telegram_id: str,
            email: str
    ) -> Dict[str, Any]:
        if not self.validate_email(email):
            return {
                'success': False,
                'message': 'Email inválido'
            }

        result = await self.user_api.delete_user(telegram_id, email)

        if result['success']:
            return {
                'success': True,
                'message': 'Conta excluída com sucesso'
            }

        logger.error(f"❌ Erro ao deletar usuário: {result.get('message')}")
        return result

    @staticmethod
    def validate_email(email: str) -> bool:
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        return re.match(regex, email, re.IGNORECASE) is not None