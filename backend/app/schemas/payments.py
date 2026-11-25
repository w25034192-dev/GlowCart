from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field


class PaymentCreateRequest(BaseModel):
    order_id: uuid.UUID


class PaymentTransactionResponse(BaseModel):
    id: uuid.UUID
    provider_event_id: str
    transaction_type: str
    status: str
    amount: Decimal
    created_at: datetime


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    method: str
    provider: str
    provider_reference: str | None
    status: str
    amount: Decimal
    currency: str
    sandbox_checkout_url: str | None = None
    transactions: list[PaymentTransactionResponse] = Field(default_factory=list)
    created_at: datetime


class PaymentWebhookRequest(BaseModel):
    provider_event_id: str = Field(min_length=3, max_length=140)
    payment_id: uuid.UUID
    status: str = Field(pattern="^(PAID|FAILED)$")


class RefundRequest(BaseModel):
    reason: str = Field(default="Admin initiated refund", max_length=500)

