import json
from typing import Optional
from uuid import UUID
from app.models import ProcessingStatus, RegisterProcessStatus


def row_to_model(row) -> ProcessingStatus:
    return ProcessingStatus(
        id=row["id"],
        status=row.get("status"),
        shipment=row.get("shipment"),
        registerProcess=row.get("register_process"),
        externalId=row.get("external_id"),
        originalText=row.get("original_text"),
        createdAt=row.get("created_at"),
        updatedAt=row.get("updated_at"),
    )


async def create_processing(conn, original_text: str):
    import json as _json
    id = None
    async with conn.transaction():
        id = await conn.fetchval(
            "INSERT INTO processing_status(original_text, status, created_at, updated_at) VALUES($1, $2, now(), now()) RETURNING id",
            original_text,
            RegisterProcessStatus.ON_QUEUE.value,
        )
    return id


async def get_processing(conn, id: UUID) -> Optional[ProcessingStatus]:
    row = await conn.fetchrow("SELECT * FROM processing_status WHERE id = $1", id)
    if not row:
        return None
    return row_to_model(row)
