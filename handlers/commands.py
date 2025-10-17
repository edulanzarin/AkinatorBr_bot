"""Handlers para comandos do bot"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.session_manager import (
    create_session,
    get_session,
    delete_session,
    has_active_session
)
from utils.keyboard import create_game_keyboard
from utils.messages import format_question, format_welcome

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /start"""
    user = update.effective_user
    await update.message.reply_text(
        format_welcome(user.first_name),
        parse_mode='HTML'
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /jogar - Inicia um novo jogo"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica se já existe sessão ativa
    if has_active_session(chat_id):
        session = get_session(chat_id)
        if session.user_id == user.id:
            await update.message.reply_text(
                "❗ Você já tem um jogo ativo!\n"
                "Use /cancelar para encerrar e começar um novo."
            )
        else:
            await update.message.reply_text(
                f"❗ Já existe um jogo ativo neste chat.\n"
                f"Aguarde o término ou peça ao usuário (ID: {session.user_id}) "
                "para usar /cancelar."
            )
        return
    
    # Cria nova sessão
    session = create_session(user.id, chat_id)
    
    try:
        # Inicia o Akinator em português - agora usando keyword arguments
        await asyncio.to_thread(session.aki.start_game, language='pt', child_mode=False, theme='c')
        session.question_count = 1
        
        # Pega a primeira pergunta
        question = session.aki.question
        
        # Envia primeira pergunta
        keyboard = create_game_keyboard()
        await update.message.reply_text(
            format_question(session, question),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        logger.info(f"🎮 Jogo iniciado - Chat: {chat_id}, User: {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar jogo: {e}")
        logger.exception(e)
        delete_session(chat_id)
        await update.message.reply_text(
            "😕 Desculpe, ocorreu um erro ao iniciar o jogo.\n"
            "Tente novamente em alguns instantes."
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /cancelar - Cancela o jogo atual"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica se existe sessão
    if not has_active_session(chat_id):
        await update.message.reply_text(
            "❗ Não há nenhum jogo ativo no momento."
        )
        return
    
    session = get_session(chat_id)
    
    # Verifica se é o dono da sessão OU se é admin do grupo
    member = await context.bot.get_chat_member(chat_id, user.id)
    is_admin = member.status in ['administrator', 'creator']
    
    if session.user_id != user.id and not is_admin:
        await update.message.reply_text(
            "❗ Apenas quem iniciou o jogo ou administradores podem cancelá-lo."
        )
        return
    
    # Remove sessão
    delete_session(chat_id)
    await update.message.reply_text(
        "✅ Jogo cancelado!\n"
        "Use /jogar para começar um novo."
    )
    
    logger.info(f"🛑 Jogo cancelado - Chat: {chat_id}, User: {user.id}")