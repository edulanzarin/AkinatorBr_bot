"""Gerenciador de sessões ativas"""

import asyncio
import logging
from typing import Dict, Optional
from models.session import AkinatorSession
from config import CLEANUP_INTERVAL

logger = logging.getLogger(__name__)

# Armazenamento de sessões ativas
# Estrutura: {chat_id: AkinatorSession}
active_sessions: Dict[int, AkinatorSession] = {}


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
    """Remove sessões expiradas periodicamente"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        expired = [
            chat_id for chat_id, session in active_sessions.items()
            if session.is_expired()
        ]
        for chat_id in expired:
            logger.info(f"⏱️ Sessão expirada removida - Chat: {chat_id}")
            delete_session(chat_id)