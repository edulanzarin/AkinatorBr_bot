"""Modelo de sessão do Akinator"""

from datetime import datetime, timedelta
from typing import Optional
from akinator import Akinator
from config import TIMEOUT, AKINATOR_LANGUAGE


class AkinatorSession:
    """Gerencia uma sessão individual do Akinator"""
    
    def __init__(self, user_id: int, chat_id: int):
        self.user_id = user_id
        self.chat_id = chat_id
        # Versão 2.0.2 do akinator
        self.aki = Akinator()
        self.last_activity = datetime.now()
        self.question_count = 0
    
    def update_activity(self):
        """Atualiza o timestamp da última atividade"""
        self.last_activity = datetime.now()
    
    def is_expired(self) -> bool:
        """Verifica se a sessão expirou"""
        return datetime.now() - self.last_activity > timedelta(seconds=TIMEOUT)
    
    def get_progress(self) -> float:
        """Retorna o progresso atual em porcentagem"""
        return float(self.aki.progression)
    
    def increment_question(self):
        """Incrementa o contador de perguntas"""
        self.question_count += 1