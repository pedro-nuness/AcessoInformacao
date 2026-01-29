from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import init_db, close_db
from app.core.mq import init_rabbit, close_rabbit, publish_message
from app import repository
from pydantic import BaseModel
from uuid import UUID
import asyncio
import json


class CreateRequest(BaseModel):
    originalText: str


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_pool = None
_rabbit = None


@app.on_event("startup")
async def startup_event():
    global _pool, _rabbit
    _pool = await init_db()
    _rabbit = await init_rabbit()


@app.on_event("shutdown")
async def shutdown_event():
    global _pool, _rabbit
    if _rabbit:
        await close_rabbit(_rabbit[0])
    await close_db(_pool)


@app.post("/processing")
async def create_processing(req: CreateRequest):
    # create processing entry (repository will create register_process and shipment)
    id = await repository.create_processing(req.originalText)
    # publish to queue
    channel = _rabbit[1]
    await publish_message(channel, "processing_queue", json.dumps({"id": str(id), "originalText": req.originalText}).encode())
    return {"id": str(id)}


@app.get("/processing/{id}")
async def get_processing(id: UUID):
    model = await repository.get_processing(id)
    if not model:
        raise HTTPException(status_code=404, detail="Not found")
    return model.dict()
