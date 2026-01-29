import asyncio
import json
from aio_pika import IncomingMessage
from app.core.db import init_db
from app.models import Status
from app.services.ai_analyzer import analyze_text
from app.core import mq
from app.repository import update_status, update_result


async def handle_message(message: IncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        id = body.get("id")
        original_text = body.get("originalText") or body.get("original_text")

        # Ensure DB initialized and use centralized repository functions
        await init_db()
        await update_status(id, Status.PROCESSING.value if hasattr(Status, 'PROCESSING') else 'processing')

        result = await analyze_text(original_text)

        # update_result will set processing status -> ready_to_ship, register_process -> completed, shipment -> ready
        await update_result(id, result)


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
