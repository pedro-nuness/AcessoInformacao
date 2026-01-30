import os
import logging
import asyncpg
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def connect(cls):
        """Inicializa a pool global se não existir."""
        if cls._pool is None:
            dsn = os.getenv("DATABASE_URL")
            try:
                cls._pool = await asyncpg.create_pool(
                    dsn,
                    min_size=int(os.getenv("DB_POOL_MIN", "5")),
                    max_size=int(os.getenv("DB_POOL_MAX", "20")),
                    command_timeout=60.0
                )
                logger.info("Database pool connection established.")
            except Exception as e:
                logger.error(f"Could not connect to database: {e}")
                raise

            last_exc = None
            for attempt in range(10):
                try:
                    migrations = Path(__file__).parents[2] / "migrations" / "processing_init.sql"
                    if migrations.exists():
                        async with cls._pool.acquire() as conn:
                            sql = migrations.read_text(encoding="utf-8")
                            await conn.execute(sql)
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    await asyncio.sleep(1)
            if last_exc:
                raise last_exc

    @classmethod
    async def disconnect(cls):
        """Fecha a pool graciosamente."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database pool connection closed.")

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        """Context manager para adquirir e liberar conexões de forma segura."""
        if cls._pool is None:
            await cls.connect()
        
        async with cls._pool.acquire() as connection:
            yield connection

db_manager = DatabaseManager()