from telegram.ext import Application, CommandHandler, MessageHandler, filters
from controllers.bot_controller import BotController
import config
import logging
import warnings
import sys

warnings.filterwarnings('ignore', category=RuntimeWarning)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


def main():
    if not hasattr(config, 'TELEGRAM_BOT_TOKEN') or not config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ Token do Telegram não configurado em 'config.py'!")
        return

    logger.info("🔧 Construindo aplicação...")

    try:
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    except Exception as e:
        logger.error(f"❌ Falha ao construir a Application: {e}")
        return

    controller = BotController()

    application.add_handler(CommandHandler("iniciar", controller.handle_start))
    application.add_handler(CommandHandler("ajuda", controller.handle_help))
    application.add_handler(CommandHandler("exclusao", controller.handle_delete_account))
    application.add_handler(CommandHandler("resumo", controller.handle_summary))
    application.add_handler(MessageHandler(filters.PHOTO, controller.handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, controller.handle_document))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        controller.handle_message
    ))

    logger.info("Bot iniciado com sucesso")
    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot finalizado!")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)