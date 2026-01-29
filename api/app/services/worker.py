import asyncio
import json
from aio_pika import IncomingMessage
from app.core.db import init_db, get_pool
from app.services.ai_analyzer import analyze_text
from app.core import mq


async def handle_message(message: IncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        id = body.get("id")
        original_text = body.get("originalText") or body.get("original_text")

        pool = get_pool()
        if pool is None:
            # initialize if not yet initialized
            await init_db()
            pool = get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE processing_status SET status = $1, updated_at = now() WHERE id = $2",
                'processing',
                id,
            )

        result = await analyze_text(original_text)

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE processing_status SET status = $1, result = $2::jsonb, updated_at = now() WHERE id = $3",
                'completed',
                json.dumps(result, default=str),
                id,
            )


async def run_worker():
    await init_db()
    connection, channel, queue = await mq.init_rabbit()
    await queue.consume(handle_message)
    print("Worker started, waiting for messages...")
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await mq.close_rabbit(connection)


if __name__ == "__main__":
    asyncio.run(run_worker())
