import asyncio
import json
from aio_pika import IncomingMessage
from app.core.db import init_db
from app.models import Status, RegisterProcessStatus
from app.services.ai_analyzer import analyze_text
from app.core import mq
from app.repository import update_status, update_result, update_register_process_status_by_processing_id


async def handle_message(message: IncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        id = body.get("id")
        original_text = body.get("originalText") or body.get("original_text")

        # Ensure DB initialized and use centralized repository functions
        await init_db()
        await update_status(id, Status.PROCESSING.value)

        try:
            result = await analyze_text(original_text)
        except Exception as e:
            # On analysis error: mark processing status as waiting human review and register_process as error
            try:
                await update_status(id, Status.WAITING_HUMAN_REVIEW.value)
                await update_register_process_status_by_processing_id(id, RegisterProcessStatus.ERROR_FATAL.value) # fatal error
            except Exception:
                # best-effort: log but don't raise further to avoid crashing consumer
                print(f"Failed to update statuses after analysis error for id={id}")
            print(f"analyze_text error for id={id}: {e}")
            return
        print( f"analyze_text success for id={id}: {result}")
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
