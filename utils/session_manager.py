"""Gerenciador de sessões ativas"""

import asyncio
import logging
from typing import Dict, Optional
from telegram.ext import Application
from models.session import AkinatorSession
from config import CLEANUP_INTERVAL

logger = logging.getLogger(__name__)

# Armazenamento de sessões ativas
# Estrutura: {chat_id: AkinatorSession}
active_sessions: Dict[int, AkinatorSession] = {}

# Referência para a aplicação do bot
_bot_app: Optional[Application] = None


def set_bot_application(app: Application):
    """Define a referência da aplicação do bot"""
    global _bot_app
    _bot_app = app


def create_session(user_id: int, chat_id: int) -> AkinatorSession:
    """Cria uma nova sessão"""
    session = AkinatorSession(user_id, chat_id)
    active_sessions[chat_id] = session
    logger.info(f"✅ Nova sessão criada - Chat: {chat_id}, User: {user_id}")
    return session


def get_session(chat_id: int) -> Optional[AkinatorSession]:
    """Retorna a sessão de um chat, se existir"""
    return active_sessions.get(chat_id)


def delete_session(chat_id: int) -> bool:
    """Remove uma sessão"""
    if chat_id in active_sessions:
        del active_sessions[chat_id]
        logger.info(f"🗑️ Sessão removida - Chat: {chat_id}")
        return True
    return False


def has_active_session(chat_id: int) -> bool:
    """Verifica se existe uma sessão ativa em um chat"""
    return chat_id in active_sessions


async def cleanup_expired_sessions():
    """Remove sessões expiradas periodicamente e notifica os chats"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        expired = [
            (chat_id, session) for chat_id, session in active_sessions.items()
            if session.is_expired()
        ]
        
        for chat_id, session in expired:
            logger.info(f"⏱️ Sessão expirada removida - Chat: {chat_id}")
            
            # Envia mensagem de notificação
            if _bot_app:
                try:
                    await _bot_app.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            "⏱️ <b>Jogo encerrado por inatividade!</b>\n\n"
                            "O tempo limite foi atingido.\n"
                            "Use /jogar para começar um novo jogo."
                        ),
                        parse_mode='HTML'
                    )
                except Exception as e:
                    logger.error(f"❌ Erro ao notificar expiração - Chat {chat_id}: {e}")
            
            delete_session(chat_id)