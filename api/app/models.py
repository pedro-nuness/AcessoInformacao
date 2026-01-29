from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class RegisterProcessStatus(str, Enum):
    NOT_QUEUED = "not_queued"       # Ainda não foi para a fila
    ON_QUEUE = "on_queue"           # RabbitMQ/Kafka
    PROCESSING = "processing"       # Worker pegou
    COMPLETED = "completed"         # Sucesso -> Gatilho para ShipmentStatus.READY
    ERROR_RETRY = "error_retry"     # Voltar para fila (incrementa retry_count)
    ERROR_FATAL = "error_fatal"     # Max_retries excedido


class ShipmentStatus(str, Enum):
    NOT_READY = "not_ready"         # Ainda processando IA
    READY = "ready"                 # Pronto para o Dispatcher pegar
    SENT = "sent"                   # Webhook recebeu 200 OK
    ERROR_RETRY = "error_retry"     # Erro 500 ou timeout (Circuit Breaker atua aqui)
    ERROR_FATAL = "error_fatal"     # Erro 4xx ou max_retries excedido

class Status(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"             # Agrega RegisterProcessStatus: ON_QUEUE, PROCESSING, RETRY
    WAITING_HUMAN_REVIEW = "waiting_human_review" # Caso a confiança da IA seja baixa ou haja erro fatal
    READY_TO_SHIP = "ready_to_ship"       # (Opcional) Momento entre o fim da IA e o início do envio
    ON_SHIPMENT = "on_shipment"           # Tentando entregar no webhook
    FINISHED = "finished"                 # Tudo concluído
    ERROR = "error"                       # Se der fatal no shipment

class Shipment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: ShipmentStatus = ShipmentStatus.NOT_READY
    attemptCount: int = 0

class Processing(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: RegisterProcessStatus = RegisterProcessStatus.NOT_QUEUED
    attemptCount: int = 0

class Result(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    confidence: float
    data: dict
class RegisterProcessEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    status: Status = Status.RECEIVED
    shipment: Shipment = Field(default_factory=Shipment)
    processing: Processing = Field(default_factory=Processing)
    externalId: Optional[str] = None
    originalText: str
    result: Optional[dict] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
