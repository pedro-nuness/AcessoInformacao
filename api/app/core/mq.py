import asyncio
import os
from typing import Optional, Tuple
from dotenv import load_dotenv
import aio_pika
from urllib.parse import urlparse

load_dotenv()

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/")

_connection: Optional[aio_pika.RobustConnection] = None
_channel: Optional[aio_pika.RobustChannel] = None
_queue: Optional[aio_pika.Queue] = None


async def init_rabbit(retries: int = 15, delay: float = 1.0) -> Tuple[aio_pika.RobustConnection, aio_pika.RobustChannel, aio_pika.Queue]:
    global _connection, _channel, _queue
    if _connection is not None:
        return _connection, _channel, _queue
    last_exc = None
    for attempt in range(retries):
        conn = None
        try:
            print(f"attempting to connect to rabbitmq (attempt {attempt+1}/{retries})")
            parsed = urlparse(RABBIT_URL)
            host = parsed.hostname or "rabbitmq"
            port = parsed.port or 5672
            try:
                fut = asyncio.open_connection(host, port)
                reader, writer = await asyncio.wait_for(fut, timeout=3.0)
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
            except Exception:
                raise ConnectionError(f"tcp connect to {host}:{port} failed")

            conn = await aio_pika.connect_robust(RABBIT_URL)
            chan = await conn.channel()

            try:
                prefetch = int(os.getenv("RABBIT_PREFETCH"))
                await chan.set_qos(prefetch_count=prefetch)
            except Exception:
                pass
            q = await chan.declare_queue("processing_queue", durable=True)
            _connection = conn
            _channel = chan
            _queue = q
            return _connection, _channel, _queue
        except Exception as e:
            last_exc = e
            if conn is not None:
                try:
                    await conn.close()
                except Exception:
                    try:
                        loop = getattr(conn, "_loop", None)
                        if loop is not None and loop.is_running():
                            asyncio.run_coroutine_threadsafe(conn.close(), loop)
                    except Exception:
                        pass
            await asyncio.sleep(delay * (1 + attempt))
    raise last_exc


async def close_rabbit(connection: Optional[aio_pika.RobustConnection] = None):
    global _connection, _channel, _queue
    conn = connection or _connection
    if conn:
        try:
            await conn.close()
        except RuntimeError:
            loop = getattr(conn, "_loop", None)
            if loop is not None and loop.is_running():
                try:
                    asyncio.run_coroutine_threadsafe(conn.close(), loop)
                except Exception:
                    pass
            else:
                try:
                    conn.close()
                except Exception:
                    pass
    _connection = None
    _channel = None
    _queue = None


async def publish_message(connection_or_channel, routing_key: str, message_bytes: bytes):
    """Publish a message. Accepts either a connection or an already-open channel.

    To be safe under high concurrency, prefer passing the connection object; a
    fresh channel will be opened per publish and closed afterwards.
    """
    try:
        default_exchange = getattr(connection_or_channel, "default_exchange", None)
    except Exception:
        default_exchange = None

    if default_exchange is not None:
        await connection_or_channel.default_exchange.publish(
            aio_pika.Message(body=message_bytes, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=routing_key,
        )
        return

    conn = connection_or_channel
    chan = None
    try:
        chan = await conn.channel()
        await chan.default_exchange.publish(
            aio_pika.Message(body=message_bytes, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key=routing_key,
        )
    finally:
        if chan is not None:
            try:
                await chan.close()
            except Exception:
                pass
