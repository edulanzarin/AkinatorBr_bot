"""Formatação de mensagens"""

from models.session import AkinatorSession


def format_question(session: AkinatorSession, question: str) -> str:
    """Formata a pergunta com informações de progresso"""
    progress = int(session.get_progress())
    
    return (
        f"📋 <b>Pergunta {session.question_count}</b>\n"
        f"📊 <b>Progresso:</b> {progress}%\n"
        f"\n"
        f"❓ <b>{question}</b>"
    )


def format_guess(name: str, description: str) -> str:
    """Formata a mensagem de palpite"""
    return (
        f"🎯 <b>EU ACHO QUE SEI!</b>\n"
        f"\n"
        f"🎭 <b>{name}</b>\n\n"
        f"📝 <i>{description}</i>\n\n"
        f"\n"
        f"Acertei?"
    )


def format_welcome(user_name: str) -> str:
    """Formata mensagem de boas-vindas"""
    return (
        f"🎮 <b>BEM-VINDO AO AKINATOR!</b>\n"
        f"Olá, <b>{user_name}</b>! 👋\n\n"
        f"Pense em um personagem real ou fictício e eu tentarei adivinhar quem é!\n\n"
        f"\n"
        f"<b>Como jogar:</b>\n"
        f"🎲 /jogar - Iniciar novo jogo\n"
        f"❌ /cancelar - Cancelar jogo atual\n\n"
        f"\n"
        f"Pronto? Use /jogar para começar!"
    )


def format_victory() -> str:
    """Mensagem de vitória do Akinator"""
    return (
        f"🎉 <b>ACERTEI NOVAMENTE!</b>\n"
        f"\n"
        f"Oba! Consegui adivinhar! 🎊\n\n"
        f"Obrigado por jogar!\n"
        f"\n"
        f"Use /jogar para uma nova partida."
    )


def format_defeat() -> str:
    """Mensagem de derrota do Akinator"""
    return (
        f"😅 <b>VOCÊ ME VENCEU!</b>\n"
        f"\n"
        f"Ah, errei dessa vez! 😔\n\n"
        f"Parabéns, você é bom! 🏆\n"
        f"\n"
        f"Use /jogar para tentar novamente."
    )