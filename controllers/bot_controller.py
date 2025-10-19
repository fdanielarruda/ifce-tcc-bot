from telegram import Update
from telegram.ext import ContextTypes
from services.transaction_service import TransactionService
from services.user_service import UserService
from messages.bot_messages import BotMessages
from middlewares.auth_middleware import auth_middleware
import logging

logger = logging.getLogger(__name__)


class BotController:
    def __init__(self):
        self.transaction_service = TransactionService()
        self.user_service = UserService()
        self.messages = BotMessages()

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        telegram_id = str(user.id)

        logger.info(f"📍 Comando /start recebido de {user.first_name} (ID: {telegram_id})")

        is_registered = await self.user_service.check_user_exists(telegram_id)

        if is_registered:
            auth_middleware.clear_cache(telegram_id)
            await update.message.reply_text(
                self.messages.get_welcome_back_message(user.first_name)
            )
        else:
            await update.message.reply_text(
                self.messages.get_registration_message(user.first_name)
            )
            context.user_data['awaiting_registration'] = True
            context.user_data['registration_step'] = 'name'

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"📍 Comando /help recebido")
        await update.message.reply_text(self.messages.get_help_message())

    @auth_middleware.require_auth(allow_commands=['start', 'help'])
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        telegram_id = str(user.id)
        message_text = update.message.text.strip()

        logger.info(f"💬 Mensagem recebida de {user.first_name}: {message_text[:50]}...")

        if context.user_data.get('awaiting_registration'):
            await self._handle_registration_flow(update, context, telegram_id, message_text)
            return

        await self._process_transaction_message(update, telegram_id, message_text)

    @auth_middleware.require_auth()
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        telegram_id = str(user.id)

        logger.info(f"📷 Foto recebida de {user.first_name}")

        await update.message.reply_text(self.messages.get_processing_message())

        try:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()

            result = await self.transaction_service.process_receipt(
                file_bytes=bytes(photo_bytes),
                mime_type='image/jpeg',
                telegram_id=telegram_id
            )

            await update.message.reply_text(result)

        except Exception as e:
            logger.error(f"❌ Erro ao processar foto: {e}")
            await update.message.reply_text(
                self.messages.get_error_message("processar a foto")
            )

    @auth_middleware.require_auth()
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        telegram_id = str(user.id)

        logger.info(f"📄 Documento recebido de {user.first_name}")

        document = update.message.document
        mime_type = document.mime_type

        if not mime_type.startswith('image/') and mime_type != 'application/pdf':
            await update.message.reply_text(
                self.messages.get_unsupported_file_message()
            )
            return

        await update.message.reply_text(self.messages.get_processing_message())

        try:
            file = await context.bot.get_file(document.file_id)
            doc_bytes = await file.download_as_bytearray()

            result = await self.transaction_service.process_receipt(
                file_bytes=bytes(doc_bytes),
                mime_type=mime_type,
                telegram_id=telegram_id
            )

            await update.message.reply_text(result)

        except Exception as e:
            logger.error(f"❌ Erro ao processar documento: {e}")
            await update.message.reply_text(
                self.messages.get_error_message("processar o documento")
            )

    async def _handle_registration_flow(
            self,
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            telegram_id: str,
            message_text: str
    ):
        step = context.user_data.get('registration_step')

        if step == 'name':
            context.user_data['user_name'] = message_text
            context.user_data['registration_step'] = 'email'
            await update.message.reply_text(
                self.messages.get_ask_email_message()
            )

        elif step == 'email':
            if not self.user_service.validate_email(message_text):
                await update.message.reply_text(
                    self.messages.get_invalid_email_message()
                )
                return

            email_exists = await self.user_service.check_email_exists(message_text)
            if email_exists:
                await update.message.reply_text(
                    self.messages.get_email_already_registered_message()
                )
                return

            name = context.user_data.get('user_name')
            result = await self.user_service.register_user(name, message_text, telegram_id)

            if result['success']:
                await update.message.reply_text(
                    self.messages.get_registration_success_message(name)
                )
                context.user_data.clear()
                auth_middleware.clear_cache(telegram_id)
            else:
                await update.message.reply_text(
                    self.messages.get_registration_error_message(result.get('message'))
                )

    async def _process_transaction_message(
            self,
            update: Update,
            telegram_id: str,
            message_text: str
    ):
        await update.message.reply_text(self.messages.get_processing_message())

        try:
            result = await self.transaction_service.process_text_transaction(
                text=message_text,
                telegram_id=telegram_id
            )
            await update.message.reply_text(result)
        except Exception as e:
            logger.error(f"❌ Erro ao processar transação: {e}")
            await update.message.reply_text(
                self.messages.get_error_message("processar a transação")
            )