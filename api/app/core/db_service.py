from typing import Optional
import json
from app.core.db import init_db, get_pool


class DBService:
    """Centralized DB access wrapper around asyncpg pool.

    Use `await DBService.get()` to obtain the singleton instance.
    This keeps all raw DB interactions in one place.
    """

    _instance: Optional["DBService"] = None

    def __init__(self, pool):
        self.pool = pool

    @classmethod
    async def get(cls) -> "DBService":
        if cls._instance is None:
            await init_db()
            pool = get_pool()
            if pool is None:
                raise RuntimeError("DB pool not initialized")
            cls._instance = DBService(pool)
        return cls._instance

    async def fetch(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *args)

    async def fetchrow(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *args)

    async def fetchval(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql, *args)

    async def execute(self, sql: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(sql, *args)

    def transaction(self):
        # Return pool-level transaction context manager
        return self.pool.transaction()
