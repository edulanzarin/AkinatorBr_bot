import os
import asyncio
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update

from handlers.commands import start, play, cancel, lock, unlock, leave_group
from handlers.callbacks import button_handler, guess_result_handler, continue_handler
from utils.session_manager import cleanup_expired_sessions, set_bot_application
from database.mongodb import connect_mongodb, close_mongodb

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Callback executado após inicialização do bot"""
    # Conecta ao MongoDB
    await connect_mongodb()
    
    # Define a referência do bot no session_manager
    set_bot_application(application)
    
    # Inicia limpeza de sessões expiradas
    asyncio.create_task(cleanup_expired_sessions())
    logger.info("🧹 Sistema de limpeza de sessões iniciado")


async def post_shutdown(application: Application) -> None:
    """Callback executado ao desligar o bot"""
    await close_mongodb()


def main():
    """Função principal"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN não configurado!")
    
    # Cria aplicação
    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Registra comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("jogar", play))
    app.add_handler(CommandHandler("cancelar", cancel))
    app.add_handler(CommandHandler("travar", lock))      # ← NOVO
    app.add_handler(CommandHandler("destravar", unlock))
    app.add_handler(CommandHandler("sair", leave_group))
    
    # Registra callbacks
    app.add_handler(CallbackQueryHandler(
    button_handler,
    pattern="^(yes|no|idk|probably|probably_not|back)$"
    ))

    app.add_handler(CallbackQueryHandler(
        guess_result_handler,
        pattern="^(correct|wrong)$"
    ))

    app.add_handler(CallbackQueryHandler(
        continue_handler,
        pattern="^(continue|give_up)$"
    ))
    
    # Inicia o bot
    logger.info("🤖 Bot Akinator iniciado com sucesso!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()