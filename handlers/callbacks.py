"""Handlers para callbacks (botões inline)"""

import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.session_manager import get_session, delete_session, has_active_session
from utils.keyboard import create_game_keyboard, create_guess_keyboard
from utils.messages import format_question, format_guess, format_victory, format_defeat
from config import GUESS_THRESHOLD

logger = logging.getLogger(__name__)

# Mapeamento de respostas para versão 2.0.2
ANSWER_MAP = {
    "yes": "yes",
    "no": "no",
    "idk": "idk",
    "probably": "probably",
    "probably_not": "probably not"
}


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para botões de resposta do jogo"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica se existe sessão ativa
    if not has_active_session(chat_id):
        await query.message.reply_text(
            "⏱️ Esta sessão expirou.\n"
            "Use /jogar para começar um novo jogo."
        )
        await query.message.delete()
        return
    
    session = get_session(chat_id)
    
    # Verifica se é o usuário correto
    if session.user_id != user.id:
        await query.answer(
            "❗ Este jogo pertence a outro usuário!",
            show_alert=True
        )
        return
    
    # Verifica timeout
    if session.is_expired():
        delete_session(chat_id)
        await query.message.reply_text(
            "⏱️ Tempo esgotado! O jogo foi encerrado por inatividade.\n"
            "Use /jogar para começar um novo jogo."
        )
        await query.message.delete()
        return
    
    session.update_activity()
    answer = query.data
    
    try:
        # Apaga mensagem anterior
        await query.message.delete()
        
        if answer == "back":
            # Volta para pergunta anterior
            if session.question_count > 1:
                await asyncio.to_thread(session.aki.back)
                session.question_count -= 1
                
                question = session.aki.question
                
                keyboard = create_game_keyboard()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=format_question(session, question),
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❗ Você já está na primeira pergunta!"
                )
                # Reenvia a pergunta atual
                keyboard = create_game_keyboard()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=format_question(session, session.aki.question),
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        
        else:
            # Processa resposta normal
            aki_answer = ANSWER_MAP.get(answer)
            if not aki_answer:
                return
            
            # Envia resposta ao Akinator (versão 2.0.2)
            await asyncio.to_thread(session.aki.answer, aki_answer)
            session.increment_question()
            
            question = session.aki.question
            
            # Verifica se deve fazer um palpite
            if session.get_progress() >= GUESS_THRESHOLD:
                await make_guess(context, chat_id, session)
            else:
                # Próxima pergunta
                keyboard = create_game_keyboard()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=format_question(session, question),
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
    
    except Exception as e:
        logger.error(f"❌ Erro ao processar resposta: {e}")
        logger.exception(e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="😕 Ocorreu um erro. O jogo foi encerrado.\n"
                 "Use /jogar para começar novamente."
        )
        delete_session(chat_id)


async def make_guess(context: ContextTypes.DEFAULT_TYPE, chat_id: int, session):
    """Faz o Akinator adivinhar o personagem"""
    try:
        # Versão 2.0.2 - o palpite está em atributos separados
        # name_proposition, description_proposition, photo
        
        if not session.aki.win:
            # Se win ainda é False, não está pronto para palpite
            keyboard = create_game_keyboard()
            await context.bot.send_message(
                chat_id=chat_id,
                text=format_question(session, session.aki.question),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            return
        
        # Monta o dicionário do palpite
        guess = {
            'name': session.aki.name_proposition or 'Desconhecido',
            'description': session.aki.description_proposition or 'Sem descrição',
            'absolute_picture_path': session.aki.photo or None
        }
        
        logger.info(f"🎯 Palpite: {guess['name']}")
        
        # Monta o texto com a informação
        text = format_guess(guess['name'], guess['description'])
        
        keyboard = create_guess_keyboard()
        
        # Verifica se tem imagem
        if guess['absolute_picture_path']:
            # Envia com imagem
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=guess['absolute_picture_path'],
                caption=text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            # Envia sem imagem
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        
        logger.info(f"🎯 Palpite enviado - Chat: {chat_id}, Personagem: {guess['name']}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao fazer palpite: {e}")
        logger.exception(e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="😕 Ocorreu um erro ao tentar adivinhar.\n"
                 "Use /jogar para tentar novamente."
        )
        delete_session(chat_id)


async def guess_result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para resultado do palpite (acertou/errou)"""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Verifica sessão
    if not has_active_session(chat_id):
        await query.message.reply_text("⏱️ Sessão expirada.")
        try:
            await query.message.delete()
        except:
            pass
        return
    
    session = get_session(chat_id)
    
    # Verifica timeout
    if session.is_expired():
        delete_session(chat_id)
        await query.message.reply_text(
            "⏱️ Tempo esgotado! O jogo foi encerrado por inatividade.\n"
            "Use /jogar para começar um novo jogo."
        )
        try:
            await query.message.delete()
        except:
            pass
        return
    
    # Verifica usuário
    if session.user_id != user.id:
        await query.answer("❗ Este jogo pertence a outro usuário!", show_alert=True)
        return
    
    result = query.data
    
    # Remove os botões da mensagem do palpite
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass
    
    # Envia resultado
    if result == "correct":
        await context.bot.send_message(
            chat_id=chat_id,
            text=format_victory(),
            parse_mode='HTML'
        )
        logger.info(f"🎉 Vitória - Chat: {chat_id}")
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=format_defeat(),
            parse_mode='HTML'
        )
        logger.info(f"😅 Derrota - Chat: {chat_id}")
    
    # Remove sessão
    delete_session(chat_id)