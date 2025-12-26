from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable, Awaitable
from functools import wraps
from apis.user_api import UserAPI
from messages.bot_messages import BotMessages
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware:
    def __init__(self):
        self.user_api = UserAPI()
        self.messages = BotMessages()
        self._user_cache = {}
        self._cache_ttl = 300

    def require_auth(
            self,
            allow_commands: list = None
    ) -> Callable:
        if allow_commands is None:
            allow_commands = []

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(
                    controller_self,
                    update: Update,
                    context: ContextTypes.DEFAULT_TYPE
            ):
                user = update.effective_user
                telegram_id = str(user.id)

                # Verifica se é um comando que não precisa de autenticação
                if update.message and update.message.text:
                    text = update.message.text.strip()
                    if text.startswith('/'):
                        command = text.split()[0][1:]
                        if command in allow_commands:
                            return await func(controller_self, update, context)

                # Verifica se está em processo de cadastro
                if context.user_data.get('awaiting_registration'):
                    return await func(controller_self, update, context)

                # Verifica autenticação
                is_authenticated = await self._check_authentication(telegram_id, user)

                if not is_authenticated:
                    await update.message.reply_text(
                        self.messages.get_not_registered_message()
                    )
                    return

                # Adiciona informações do usuário ao context para uso posterior
                context.user_data['authenticated'] = True
                context.user_data['telegram_id'] = telegram_id

                # Executa a função original
                return await func(controller_self, update, context)

            return wrapper

        return decorator

    async def _check_authentication(self, telegram_id: str, user) -> bool:
        try:
            # Verifica cache primeiro
            if telegram_id in self._user_cache:
                cached_data = self._user_cache[telegram_id]

                import time
                if time.time() - cached_data['timestamp'] < self._cache_ttl:
                    logger.debug(f"📦 Usuário {telegram_id} encontrado no cache")
                    return cached_data['is_authenticated']

            # Consulta a API
            logger.info(f"🔍 Verificando autenticação do usuário {telegram_id} na API")
            result = await self.user_api.check_user('telegram_id', telegram_id)

            if result['success']:
                users = result.get('data', {}).get('users', [])
                is_authenticated = bool(users)

                import time
                self._user_cache[telegram_id] = {
                    'is_authenticated': is_authenticated,
                    'timestamp': time.time(),
                    'user_data': users[0] if users else None
                }

                if is_authenticated:
                    user_name = users[0].get('name', user.first_name)
                    logger.info(f"✅ Usuário autenticado: {user_name} ({telegram_id})")
                else:
                    logger.warning(f"⚠️ Usuário não encontrado: {telegram_id}")

                return is_authenticated

            logger.error(f"Erro ao verificar usuário: {result.get('message')}")
            return False

        except Exception as e:
            logger.error(f"Erro no middleware de autenticação: {e}", exc_info=True)
            return False

    def clear_cache(self, telegram_id: str = None):
        if telegram_id:
            if telegram_id in self._user_cache:
                del self._user_cache[telegram_id]
                logger.info(f"🗑️ Cache limpo para usuário {telegram_id}")
        else:
            self._user_cache.clear()
            logger.info("🗑️ Todo o cache de autenticação foi limpo")

    def get_cached_user_data(self, telegram_id: str) -> dict:
        if telegram_id in self._user_cache:
            return self._user_cache[telegram_id].get('user_data')
        return None


auth_middleware = AuthMiddleware()