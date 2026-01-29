import asyncio
import os
import json
import time
import aiohttp
import logging
import traceback
from app.core.db import init_db
from app.models import Status, ShipmentStatus, RegisterProcessStatus
from app.repository import (
    fetch_pending_shipments,
    mark_shipment_sent,
    update_register_process_status_by_processing_id,
    set_shipment_status_by_processing_id,
    get_shipment_attempts_by_processing_id,
    update_status,
)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DISPATCH_INTERVAL = int(os.getenv("DISPATCH_INTERVAL", "30"))  # Intervalo em segundos entre verificações de envios pendentes

CB_FAILURE_THRESHOLD = int(os.getenv("CB_FAILURE_THRESHOLD", "3")) # Número de falhas para abrir o circuito
CB_RECOVERY_TIMEOUT = int(os.getenv("CB_RECOVERY_TIMEOUT", "60"))   # Tempo em segundos para tentar fechar o circuito novamente
CB_HALF_OPEN_MAX_CALLS = int(os.getenv("CB_HALF_OPEN_MAX_CALLS", "1")) # Número de chamadas permitidas no estado half-open


class CircuitBreaker:
    """Simple in-memory async-friendly circuit breaker.

    States:
      - CLOSED: allow requests, count failures
      - OPEN: block requests until recovery timeout
      - HALF_OPEN: allow a small number of trial requests
    """

    def __init__(self, failure_threshold=3, recovery_timeout=60, half_open_max_calls=1):
        self._failure_threshold = int(failure_threshold)
        self._recovery_timeout = int(recovery_timeout)
        self._half_open_max_calls = int(half_open_max_calls)
        self._state = "CLOSED"
        self._failure_count = 0
        self._opened_at = None
        self._half_open_calls = 0

    def _now(self):
        return time.monotonic()

    def allow(self):
        if self._state == "OPEN":
            # still cooling down?
            if (self._now() - self._opened_at) >= self._recovery_timeout:
                # move to half-open and allow trial
                self._state = "HALF_OPEN"
                self._half_open_calls = 0
                return True
            return False
        if self._state == "HALF_OPEN":
            if self._half_open_calls < self._half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False
        # CLOSED
        return True

    def record_success(self):
        self._failure_count = 0
        self._state = "CLOSED"
        self._opened_at = None
        self._half_open_calls = 0

    def record_failure(self):
        self._failure_count += 1
        if self._failure_count >= self._failure_threshold:
            self._state = "OPEN"
            self._opened_at = self._now()

    @property
    def state(self):
        return self._state

async def dispatch_pending():
    await init_db()
    cb = CircuitBreaker(
        failure_threshold=CB_FAILURE_THRESHOLD,
        recovery_timeout=CB_RECOVERY_TIMEOUT,
        half_open_max_calls=CB_HALF_OPEN_MAX_CALLS,
    )

    while True:
        rows = await fetch_pending_shipments()
        if not rows:
            await asyncio.sleep(DISPATCH_INTERVAL)
            continue

        for row in rows:
            proc_id = row["processing_id"]
            result = row["result"]
            shipment = row["shipment"]

            if not WEBHOOK_URL:
                logging.warning("WEBHOOK_URL not configured; skipping dispatch")
                break

            if not cb.allow():
                logging.info(f"Circuit open; skipping dispatch for id={proc_id}")
                continue

            # mark processing as on_shipment
            try:
                await update_status(proc_id, Status.ON_SHIPMENT.value)
            except Exception:
                logging.exception(f"Failed to mark processing {proc_id} as ON_SHIPMENT")

            # prepare payload ensuring UUIDs are converted to strings
            payload = {"id": str(proc_id), "result": result, "shipment": shipment}
            try:
                payload_json = json.dumps(payload, default=str)
            except Exception as ser_e:
                logging.exception(f"Failed to JSON-serialize payload for id={proc_id}: {ser_e}")
                # persist retryable error and continue
                try:
                    await set_shipment_status_by_processing_id(proc_id, ShipmentStatus.ERROR_RETRY.value, increment_attempt=True)
                    await update_status(proc_id, Status.ERROR.value)
                    await update_register_process_status_by_processing_id(proc_id, RegisterProcessStatus.ERROR_RETRY.value)
                except Exception:
                    logging.exception(f"Failed to persist serialization error state for id={proc_id}")
                cb.record_failure()
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Content-Type": "application/json"}
                    resp = await session.post(WEBHOOK_URL, data=payload_json, headers=headers)
                    resp_text = await resp.text()
                    if 200 <= resp.status < 300:
                        await mark_shipment_sent(proc_id)
                        # finalize processing
                        await update_status(proc_id, Status.FINISHED.value)
                        await update_register_process_status_by_processing_id(proc_id, RegisterProcessStatus.COMPLETED.value)
                        cb.record_success()
                        logging.info(f"Dispatched shipment for id={proc_id}: status={resp.status}")
                    else:
                        # non-2xx responses count as failures
                        cb.record_failure()
                        logging.error(f"Dispatch failed for id={proc_id}: status={resp.status}, body={resp_text}, CB={cb.state}")
                        # 5xx -> retryable
                        if resp.status >= 500:
                            try:
                                await set_shipment_status_by_processing_id(proc_id, ShipmentStatus.ERROR_RETRY.value, increment_attempt=True)
                                await update_status(proc_id, Status.ERROR.value)
                                await update_register_process_status_by_processing_id(proc_id, RegisterProcessStatus.ERROR_RETRY.value)
                            except Exception:
                                logging.exception(f"Failed to persist retryable error state for id={proc_id}")
                        else:
                            # 4xx -> fatal
                            try:
                                await set_shipment_status_by_processing_id(proc_id, ShipmentStatus.ERROR_FATAL.value, increment_attempt=False)
                                await update_status(proc_id, Status.ERROR.value)
                                await update_register_process_status_by_processing_id(proc_id, RegisterProcessStatus.ERROR_FATAL.value)
                            except Exception:
                                logging.exception(f"Failed to persist fatal error state for id={proc_id}")
            except Exception as e:
                cb.record_failure()
                logging.exception(f"Exception while dispatching id={proc_id}: {e} (CB state={cb.state})")
                # network/exception -> treat as retryable
                try:
                    await set_shipment_status_by_processing_id(proc_id, ShipmentStatus.ERROR_RETRY.value, increment_attempt=True)
                    await update_status(proc_id, Status.ERROR.value)
                    await update_register_process_status_by_processing_id(proc_id, RegisterProcessStatus.ERROR_RETRY.value)
                except Exception:
                    logging.exception(f"Failed to persist error state for id={proc_id}")

        await asyncio.sleep(DISPATCH_INTERVAL)


if __name__ == "__main__":
    asyncio.run(dispatch_pending())