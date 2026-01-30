import asyncio
import json
import signal
from venv import logger
from aio_pika import IncomingMessage
import asyncpg
from app.models import Status, RegisterProcessStatus
from app.services.ai_analyzer import analyze_text
from app.core import mq
from app.repository import update_status, update_result, update_register_process_status_by_processing_id


async def handle_message(message: IncomingMessage):
    # use explicit ack/nack handling so we can requeue when Postgres is overloaded
    async with message.process(): # Gerencia ACK/NACK automaticamente
        try:
            body = json.loads(message.body.decode()) 
            proc_id = body.get("id")
            text = body.get("originalText") 

            # 1. Marcar como processando
            await update_status(proc_id, Status.PROCESSING.value)

            # 2. IA - Processamento intensivo fora do loop de IO se necessário
            result = await analyze_text(text) 

            # 3. Salvar resultado e finalizar
            await update_result(proc_id, result)
            
            logger.info(f"Processed successfully: {proc_id}")

        except Exception as e:
            logger.error(f"Error processing {proc_id}: {e}")

async def run_worker():
    connection, channel, queue = await mq.init_rabbit()

    # Setup graceful shutdown handling
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _set_stop():
        stop_event.set()

    try:
        for s in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(s, _set_stop)
            except NotImplementedError:
                # add_signal_handler may not be implemented on Windows event loop
                pass
    except Exception:
        pass

    await queue.consume(handle_message)
    print("Worker started, waiting for messages...")
    try:
        await stop_event.wait()
    finally:
        # close the connection cleanly on the same loop
        await mq.close_rabbit(connection)


if __name__ == "__main__":
    asyncio.run(run_worker())
