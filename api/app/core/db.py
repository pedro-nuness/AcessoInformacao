import asyncio
from pathlib import Path
from typing import Optional
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

_pool: Optional[asyncpg.pool.Pool] = None


async def init_db(retries: int = 8, delay: float = 1.0):
    global _pool
    if _pool is not None:
        return _pool
    last_exc = None
    # Allow controlling pool size via env vars to avoid exhausting Postgres max_connections
    min_size = int(os.getenv("DB_POOL_MIN", "1"))
    max_size = int(os.getenv("DB_POOL_MAX", "5"))
    for attempt in range(retries):
        try:
            _pool = await asyncpg.create_pool(DATABASE_URL, min_size=min_size, max_size=max_size)
            # Run migrations if present
            migrations = Path(__file__).parents[2] / "migrations" / "processing_init.sql"
            if migrations.exists():
                async with _pool.acquire() as conn:
                    sql = migrations.read_text(encoding="utf-8")
                    await conn.execute(sql)
            return _pool
        except Exception as e:
            last_exc = e
            await asyncio.sleep(delay * (1 + attempt))
    raise last_exc


def get_pool() -> Optional[asyncpg.pool.Pool]:
    return _pool


async def close_db(pool: Optional[asyncpg.pool.Pool] = None):
    global _pool
    p = pool or _pool
    if p:
        await p.close()
    _pool = None
