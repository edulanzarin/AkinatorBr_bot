"""Criação de teclados inline"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_game_keyboard() -> InlineKeyboardMarkup:
    """Cria o teclado de respostas do jogo"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim", callback_data="yes"),
            InlineKeyboardButton("❌ Não", callback_data="no")
        ],
        [
            InlineKeyboardButton("🤔 Não sei", callback_data="idk")
        ],
        [
            InlineKeyboardButton("👍 Provavelmente sim", callback_data="probably"),
            InlineKeyboardButton("👎 Provavelmente não", callback_data="probably_not")
        ],
        [
            InlineKeyboardButton("↩️ Corrigir resposta", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_guess_keyboard() -> InlineKeyboardMarkup:
    """Cria o teclado de confirmação do palpite"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Acertou!", callback_data="correct"),
            InlineKeyboardButton("❌ Errou", callback_data="wrong")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_continue_keyboard() -> InlineKeyboardMarkup:
    """Cria o teclado para perguntar se quer continuar após erro"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Continuar tentando", callback_data="continue"),
            InlineKeyboardButton("❌ Desistir", callback_data="give_up")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)