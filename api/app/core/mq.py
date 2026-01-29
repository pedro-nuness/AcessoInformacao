import asyncio
import os
from typing import Optional, Tuple
from dotenv import load_dotenv
import aio_pika

load_dotenv()

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[aio_pika.RobustChannel] = None
_queue: Optional[aio_pika.Queue] = None


async def init_rabbit(retries: int = 8, delay: float = 1.0) -> Tuple[aio_pika.RobustConnection, aio_pika.RobustChannel, aio_pika.Queue]:
    global _connection, _channel, _queue
    if _connection is not None:
        return _connection, _channel, _queue
    last_exc = None
    for attempt in range(retries):
        try:
            _connection = await aio_pika.connect_robust(RABBIT_URL)
            _channel = await _connection.channel()
            _queue = await _channel.declare_queue("processing_queue", durable=True)
            return _connection, _channel, _queue
        except Exception as e:
            last_exc = e
            await asyncio.sleep(delay * (1 + attempt))
    raise last_exc


async def close_rabbit(connection: Optional[aio_pika.RobustConnection] = None):
    global _connection, _channel, _queue
    conn = connection or _connection
    if conn:
        await conn.close()
    _connection = None
    _channel = None
    _queue = None


async def publish_message(channel: aio_pika.RobustChannel, routing_key: str, message_bytes: bytes):
    await channel.default_exchange.publish(
        aio_pika.Message(body=message_bytes, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
        routing_key=routing_key,
    )
