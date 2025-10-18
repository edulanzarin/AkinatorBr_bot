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
from utils.permissions import is_user_admin
from database.mongodb import save_user_id, lock_chat, unlock_chat, is_chat_locked

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /start"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Verifica se o chat está travado
    if await is_chat_locked(chat_id):
        return
    
    await save_user_id(user.id)
    
    await update.message.reply_text(
        format_welcome(user.first_name),
        parse_mode='HTML'
    )


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /jogar - Inicia um novo jogo"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica se o chat está travado
    if await is_chat_locked(chat_id):
        await update.message.reply_text(
            "🔒 O bot está travado neste grupo.\n"
            "Apenas administradores podem usar /destravar."
        )
        return
    
    await save_user_id(user.id)
    
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
                f"Aguarde o término ou peça ao usuário que está jogando "
                "para usar /cancelar."
            )
        return
    
    # Cria nova sessão
    session = create_session(user.id, chat_id)
    
    try:
        # Inicia o Akinator em português
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
    
    # Verifica se o chat está travado
    if await is_chat_locked(chat_id):
        await update.message.reply_text(
            "🔒 O bot está travado neste grupo.\n"
            "Apenas administradores podem usar /destravar."
        )
        return
    
    await save_user_id(user.id)
    
    # Verifica se existe sessão
    if not has_active_session(chat_id):
        await update.message.reply_text(
            "❗ Não há nenhum jogo ativo no momento."
        )
        return
    
    session = get_session(chat_id)
    
    # Verifica se é o dono da sessão OU se é admin do grupo
    is_admin = await is_user_admin(update, context)
    
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


async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /travar - Trava o bot (apenas admins)"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica se é admin
    if not await is_user_admin(update, context):
        await update.message.reply_text(
            "❗ Apenas administradores podem travar o bot."
        )
        return
    
    await save_user_id(user.id)
    
    # Verifica se já está travado
    if await is_chat_locked(chat_id):
        await update.message.reply_text(
            "🔒 O bot já está travado neste grupo."
        )
        return
    
    # Cancela jogo ativo se houver
    if has_active_session(chat_id):
        delete_session(chat_id)
    
    # Trava o chat
    await lock_chat(chat_id)
    
    await update.message.reply_text(
        "🔒 <b>Bot travado com sucesso!</b>\n\n"
        "O bot não responderá a nenhum comando neste grupo até ser destravado.\n"
        "Use /destravar para liberar.",
        parse_mode='HTML'
    )
    
    logger.info(f"🔒 Bot travado - Chat: {chat_id}, Admin: {user.id}")


async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler do comando /destravar - Destrava o bot (apenas admins)"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica se é admin
    if not await is_user_admin(update, context):
        await update.message.reply_text(
            "❗ Apenas administradores podem destravar o bot."
        )
        return
    
    await save_user_id(user.id)
    
    # Verifica se está travado
    if not await is_chat_locked(chat_id):
        await update.message.reply_text(
            "🔓 O bot não está travado neste grupo."
        )
        return
    
    # Destrava o chat
    await unlock_chat(chat_id)
    
    await update.message.reply_text(
        "🔓 <b>Bot destravado com sucesso!</b>\n\n"
        "O bot voltou a funcionar normalmente.\n"
        "Use /jogar para começar um jogo.",
        parse_mode='HTML'
    )
    
    logger.info(f"🔓 Bot destravado - Chat: {chat_id}, Admin: {user.id}")