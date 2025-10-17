"""Conexão e operações com MongoDB"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

logger = logging.getLogger(__name__)

# Cliente MongoDB
_mongo_client: Optional[AsyncIOMotorClient] = None
_db = None
_users_collection = None


async def connect_mongodb():
    """Conecta ao MongoDB"""
    global _mongo_client, _db, _users_collection
    
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        logger.warning("⚠️ MONGODB_URI não configurado! IDs não serão salvos.")
        return False
    
    try:
        _mongo_client = AsyncIOMotorClient(mongo_uri)
        _db = _mongo_client.akinator_bot
        _users_collection = _db.users
        
        # Cria índice único para user_id
        await _users_collection.create_index("user_id", unique=True)
        
        logger.info("✅ MongoDB conectado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar MongoDB: {e}")
        return False


async def save_user_id(user_id: int) -> bool:
    """Salva o ID do usuário no MongoDB (apenas se não existir)"""
    if _users_collection is None:  # ← MUDANÇA AQUI
        return False
    
    try:
        # insert_one com upsert=True (insere apenas se não existir)
        await _users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )
        logger.info(f"💾 User ID salvo: {user_id}")
        return True
    except Exception as e:
        # Ignora erro de duplicata (significa que já existe)
        if "duplicate key error" not in str(e).lower():
            logger.error(f"❌ Erro ao salvar user_id {user_id}: {e}")
        return False


async def get_total_users() -> int:
    """Retorna o total de usuários únicos"""
    if _users_collection is None:  # ← MUDANÇA AQUI
        return 0
    
    try:
        count = await _users_collection.count_documents({})
        return count
    except Exception as e:
        logger.error(f"❌ Erro ao contar usuários: {e}")
        return 0


async def close_mongodb():
    """Fecha a conexão com MongoDB"""
    global _mongo_client
    if _mongo_client is not None:  # ← MUDANÇA AQUI
        _mongo_client.close()
        logger.info("🔌 MongoDB desconectado")