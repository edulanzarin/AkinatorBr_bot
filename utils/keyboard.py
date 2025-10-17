"""Utilitários para criação de teclados inline"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_game_keyboard() -> InlineKeyboardMarkup:
    """Cria o teclado inline com as opções do jogo"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim", callback_data="yes"),
            InlineKeyboardButton("❌ Não", callback_data="no"),
        ],
        [
            InlineKeyboardButton("🤔 Não sei", callback_data="idk"),
        ],
        [
            InlineKeyboardButton("👍 Provavelmente sim", callback_data="probably"),
            InlineKeyboardButton("👎 Provavelmente não", callback_data="probably_not"),
        ],
        [
            InlineKeyboardButton("↩️ Corrigir resposta", callback_data="back"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_guess_keyboard() -> InlineKeyboardMarkup:
    """Cria o teclado para confirmar/negar o palpite"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Sim, acertou!", callback_data="correct"),
            InlineKeyboardButton("❌ Não, errou", callback_data="wrong")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)