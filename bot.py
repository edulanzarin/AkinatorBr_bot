import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update

from handlers.commands import start, play, cancel
from handlers.callbacks import button_handler, guess_result_handler
from utils.session_manager import cleanup_expired_sessions

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Callback executado após inicialização do bot"""
    # Inicia limpeza de sessões expiradas
    asyncio.create_task(cleanup_expired_sessions())
    logger.info("🧹 Sistema de limpeza de sessões iniciado")


def main():
    """Função principal"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN não configurado!")
    
    # Cria aplicação
    app = Application.builder().token(token).post_init(post_init).build()
    
    # Registra comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jogar", play))
    app.add_handler(CommandHandler("cancelar", cancel))
    
    # Registra callbacks
    app.add_handler(CallbackQueryHandler(
        button_handler,
        pattern="^(yes|no|idk|probably|probably_not|back)$"
    ))
    
    app.add_handler(CallbackQueryHandler(
        guess_result_handler,
        pattern="^(correct|wrong)$"
    ))
    
    # Inicia o bot
    logger.info("🤖 Bot Akinator iniciado com sucesso!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()