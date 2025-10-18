"""Utilitários para verificar permissões"""

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Verifica se o usuário é administrador do grupo ou tem permissões de admin"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        
        # Criador do grupo
        if member.status == ChatMember.OWNER:
            return True
        
        # Administrador oficial
        if member.status == ChatMember.ADMINISTRATOR:
            return True
        
        # Verifica se tem permissões específicas de admin (mesmo que não seja admin oficial)
        # Algumas permissões que indicam poder de administração:
        if member.status == ChatMember.MEMBER:
            # Se for membro comum mas tem alguma permissão de admin, considera como admin
            if hasattr(member, 'can_delete_messages') and member.can_delete_messages:
                return True
            if hasattr(member, 'can_restrict_members') and member.can_restrict_members:
                return True
            if hasattr(member, 'can_promote_members') and member.can_promote_members:
                return True
            if hasattr(member, 'can_manage_chat') and member.can_manage_chat:
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar permissões - User {user_id} no Chat {chat_id}: {e}")
        return False