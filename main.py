from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handlers import BotHandlers
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

    handlers = BotHandlers()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.processar_mensagem))

    logger.info("✅ Bot iniciado com sucesso!")
    logger.info("💬 Aguardando mensagens...")
    logger.info("🛑 Pressione Ctrl+C para parar")

    application.run_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot finalizado!")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)