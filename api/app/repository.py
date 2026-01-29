import json
from typing import Optional, List, Dict
from uuid import UUID
from app.models import (
    RegisterProcessEvent,
    RegisterProcessStatus,
    Status,
    ShipmentStatus,
    Shipment,
    Processing,
)
from app.core.db_service import DBService


def row_to_model(row) -> Optional[RegisterProcessEvent]:
    if not row:
        return None
    shipment = None
    if row.get("shipment_id"):
        shipment = Shipment(
            id=row.get("shipment_id"),
            status=ShipmentStatus(row.get("shipment_status")),
            attemptCount=row.get("shipment_attempt_count") or 0,
        )
    else:
        shipment = Shipment()

    register_process = None
    if row.get("register_process_id"):
        register_process = Processing(
            id=row.get("register_process_id"),
            status=RegisterProcessStatus(row.get("register_status")),
            attemptCount=row.get("register_attempt_count") or 0,
        )
    else:
        register_process = Processing()

    return RegisterProcessEvent(
        id=row["id"],
        status=Status(row.get("status")) if row.get("status") is not None else Status.RECEIVED,
        shipment=shipment,
        processing=register_process,
        externalId=row.get("external_id"),
        originalText=row.get("original_text"),
        createdAt=row.get("created_at"),
        updatedAt=row.get("updated_at"),
    )


async def create_processing(original_text: str, external_id: Optional[str] = None) -> UUID:
    db = await DBService.get()
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            # create processing (was register_process)
            register_id = await conn.fetchval(
                "INSERT INTO processing(status, attempt_count, created_at, updated_at) VALUES($1, $2, now(), now()) RETURNING id",
                RegisterProcessStatus.NOT_QUEUED.value,
                0,
            )
            # create shipment
            shipment_id = await conn.fetchval(
                "INSERT INTO shipment(status, attempt_count, created_at, updated_at) VALUES($1, $2, now(), now()) RETURNING id",
                ShipmentStatus.NOT_READY.value,
                0,
            )
            # create processing_status
            proc_id = await conn.fetchval(
                "INSERT INTO register_process_event(original_text, external_id, status, register_process_id, shipment_id, created_at, updated_at) VALUES($1, $2, $3, $4, $5, now(), now()) RETURNING id",
                original_text,
                external_id,
                Status.RECEIVED.value,
                register_id,
                shipment_id,
            )
    return proc_id


async def get_processing(id: UUID) -> Optional[RegisterProcessEvent]:
    db = await DBService.get()
    row = await db.fetchrow(
        "SELECT p.*, r.status as register_status, r.attempt_count as register_attempt_count, r.id as register_process_id, s.status as shipment_status, s.attempt_count as shipment_attempt_count, s.id as shipment_id FROM register_process_event p LEFT JOIN processing r ON r.id = p.register_process_id LEFT JOIN shipment s ON s.id = p.shipment_id WHERE p.id = $1",
        id,
    )
    if not row:
        return None
    return row_to_model(row)


async def update_status(id: UUID, status: str):
    db = await DBService.get()
    return await db.execute("UPDATE register_process_event SET status = $1, updated_at = now() WHERE id = $2", status, id)


async def update_result(id: UUID, result: dict):
    """When worker finishes analysis: set processing_status.result, mark processing as READY_TO_SHIP,
    set register_process to COMPLETED and shipment to READY.
    """
    db = await DBService.get()
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow("SELECT register_process_id, shipment_id FROM register_process_event WHERE id = $1", id)
            if not row:
                return None
            register_id = row.get("register_process_id")
            shipment_id = row.get("shipment_id")

            await conn.execute(
                "UPDATE register_process_event SET status = $1, result = $2::jsonb, updated_at = now() WHERE id = $3",
                Status.READY_TO_SHIP.value,
                json.dumps(result, default=str),
                id,
            )

            if register_id:
                await conn.execute(
                    "UPDATE processing SET status = $1, updated_at = now() WHERE id = $2",
                        RegisterProcessStatus.COMPLETED.value,
                        register_id,
                )

            if shipment_id:
                await conn.execute(
                    "UPDATE shipment SET status = $1, updated_at = now() WHERE id = $2",
                    ShipmentStatus.READY.value,
                    shipment_id,
                )
    return True


async def fetch_pending_shipments() -> List[Dict]:
    db = await DBService.get()
    rows = await db.fetch(
        "SELECT p.id as processing_id, p.result, s.id as shipment_id, s.status as shipment_status, s.attempt_count as shipment_attempt_count FROM register_process_event p JOIN shipment s ON s.id = p.shipment_id WHERE s.status != 'sent' AND p.result IS NOT NULL"
    )
    out = []
    for r in rows:
        out.append(
            {
                "processing_id": r.get("processing_id"),
                "result": r.get("result"),
                "shipment": {"id": r.get("shipment_id"), "status": r.get("shipment_status"), "attemptCount": r.get("shipment_attempt_count")},
            }
        )
    return out


async def mark_shipment_sent(processing_id: UUID):
    db = await DBService.get()
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT shipment_id FROM register_process_event WHERE id = $1", processing_id)
        if not row:
            return None
        shipment_id = row.get("shipment_id")
        if shipment_id:
            return await conn.execute("UPDATE shipment SET status = $1, updated_at = now() WHERE id = $2", ShipmentStatus.SENT.value, shipment_id)
    return None


async def update_register_process_status_by_processing_id(processing_id: UUID, status: str):
    """Update register_process.status given a processing_status id."""
    db = await DBService.get()
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT register_process_id FROM register_process_event WHERE id = $1", processing_id)
        if not row:
            return None
        register_id = row.get("register_process_id")
        if register_id:
            return await conn.execute("UPDATE register_process SET status = $1, updated_at = now() WHERE id = $2", status, register_id)
    return None


async def set_shipment_status_by_processing_id(processing_id: UUID, shipment_status: str, increment_attempt: bool = False):
    """Set shipment.status (and optionally increment attempt_count) for the shipment related to processing_status id."""
    db = await DBService.get()
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow("SELECT shipment_id FROM register_process_event WHERE id = $1", processing_id)
            if not row:
                return None
            shipment_id = row.get("shipment_id")
            if not shipment_id:
                return None
            if increment_attempt:
                return await conn.execute(
                    "UPDATE shipment SET status = $1, attempt_count = COALESCE(attempt_count,0) + 1, updated_at = now() WHERE id = $2",
                    shipment_status,
                    shipment_id,
                )
            else:
                return await conn.execute(
                    "UPDATE shipment SET status = $1, updated_at = now() WHERE id = $2",
                    shipment_status,
                    shipment_id,
                )


async def get_shipment_attempts_by_processing_id(processing_id: UUID):
    db = await DBService.get()
    row = await db.fetchrow("SELECT s.attempt_count as shipment_attempt_count FROM register_process_event p JOIN shipment s ON s.id = p.shipment_id WHERE p.id = $1", processing_id)
    if not row:
        return None
    return row.get("shipment_attempt_count")
