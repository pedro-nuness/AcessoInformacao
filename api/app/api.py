from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from app.core.mq import init_rabbit, close_rabbit, publish_message
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.db import db_manager
from app import repository
from app.services.ai_analyzer import analyze_text
from app.models import Status, RegisterProcessStatus, ShipmentStatus
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
import asyncio
import json

class CreateRequest(BaseModel):
    originalText: str
    externalId: Optional[str] = None

_rabbit = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa recursos de forma centralizada
    await db_manager.connect()  
    global _rabbit
    _rabbit = await init_rabbit()         
    yield
    # Limpeza graciosa no desligamento
    _rabbit = await close_rabbit()        
    await db_manager.disconnect() 

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

logger = logging.getLogger("processing_api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def _bg_publish(conn, payload):
        try:
            await publish_message(conn, "processing_queue", payload)
        except Exception as e:
            print(f"background publish failed for id={id}: {e}")

@app.post("/processing")
async def create_processing(req: CreateRequest):
    start = time.monotonic()
    id = await repository.create_processing(req.originalText, req.externalId)
    connection = _rabbit[0]
    
    message_bytes = json.dumps({"id": str(id), "originalText": req.originalText}).encode()
    try:
        asyncio.create_task(_bg_publish(connection, message_bytes))
    except Exception as e:
        print(f"failed to schedule background publish for id={id}: {e}")

    logger.info(f"create_processing id={id} duration_ms={(time.monotonic()-start)*1000:.1f} returned=accepted")
    return JSONResponse(status_code=202, content={"id": str(id)})
     
@app.post("/processing/now")
async def create_and_process_now(req: CreateRequest):
    start = time.monotonic()
    try:
        result = await analyze_text(req.originalText)

        duration_ms = (time.monotonic() - start) * 1000
        logger.info(f"create_and_process_now inline duration_ms={duration_ms:.1f} returned=ok")
        return JSONResponse(status_code=200, content={"result": result})

    except Exception as e:
        logger.exception(f"Inline processing failed: {e}")
        raise HTTPException(status_code=500, detail="Processing failed")


@app.get("/processing/{id}")
async def get_processing(id: UUID):
    start = time.monotonic()
    model = await repository.get_processing(id)
    duration_ms = (time.monotonic() - start) * 1000
    if not model:
        logger.info(f"get_processing id={id} duration_ms={duration_ms:.1f} returned=404")
        raise HTTPException(status_code=404, detail="Not found")
    logger.info(f"get_processing id={id} duration_ms={duration_ms:.1f} status={model.shipment.status}")
    return model.model_dump()

@app.get("/processing/external/{external_id}")
async def get_processing_by_external(external_id: str):
    start = time.monotonic()
    models = await repository.get_processing_by_external_id(external_id)
    duration_ms = (time.monotonic() - start) * 1000
    if not models:
        logger.info(f"get_processing_by_external externalId={external_id} duration_ms={duration_ms:.1f} returned=404")
        raise HTTPException(status_code=404, detail="Not found")
    # if only one result, return single object, otherwise return list
    if len(models) == 1:
        model = models[0]
        logger.info(f"get_processing_by_external externalId={external_id} duration_ms={duration_ms:.1f} status={model.shipment.status}")
        return model.model_dump()
    else:
        logger.info(f"get_processing_by_external externalId={external_id} duration_ms={duration_ms:.1f} returned={len(models)} items")
        return [m.model_dump() for m in models]