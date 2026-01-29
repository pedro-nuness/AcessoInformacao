from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RegisterProcessStatus(str, Enum):
    ON_QUEUE = "on_queue"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR_RETRY = "error_retry"
    ERROR_FATAL = "error_fatal"


class ShipmentStatus(str, Enum):
    NOT_READY = "not_ready"
    READY = "ready"
    SENDING = "sending"
    SENT = "sent"
    ERROR_RETRY = "error_retry"
    ERROR_FATAL = "error_fatal"


class Shipment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: ShipmentStatus = ShipmentStatus.NOT_READY
    attemptCount: int = 0


class RegisterProcess(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: RegisterProcessStatus = RegisterProcessStatus.ON_QUEUE
    attemptCount: int = 0


class Result(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    confidence: float
    data: dict


class ProcessingStatus(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: RegisterProcessStatus = RegisterProcessStatus.ON_QUEUE
    shipment: Shipment = Field(default_factory=Shipment)
    registerProcess: RegisterProcess = Field(default_factory=RegisterProcess)
    externalId: Optional[str] = None
    originalText: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
