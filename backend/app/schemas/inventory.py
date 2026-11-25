from datetime import date, datetime
import uuid
from pydantic import BaseModel, Field


class BatchReceiveRequest(BaseModel):
    variant_id: uuid.UUID
    batch_number: str = Field(min_length=2, max_length=100)
    manufacture_date: date
    expiry_date: date
    quantity: int = Field(gt=0)
    received_date: date | None = None
    reason: str = "Stock batch received"


class InventoryAdjustRequest(BaseModel):
    variant_id: uuid.UUID
    quantity_delta: int
    reason: str = Field(min_length=3, max_length=500)
    low_stock_threshold: int | None = Field(default=None, ge=0)


class InventoryItemResponse(BaseModel):
    variant_id: uuid.UUID
    sku: str
    product_name: str
    variant_label: str
    available_quantity: int
    reserved_quantity: int
    sellable_quantity: int
    low_stock_threshold: int
    is_low_stock: bool
    is_out_of_stock: bool
    updated_at: datetime


class BatchResponse(BaseModel):
    id: uuid.UUID
    variant_id: uuid.UUID
    sku: str
    product_name: str
    batch_number: str
    manufacture_date: date
    expiry_date: date
    initial_quantity: int
    remaining_quantity: int
    received_date: date
    is_expired: bool


class MovementResponse(BaseModel):
    id: uuid.UUID
    variant_id: uuid.UUID
    batch_id: uuid.UUID | None
    actor_id: uuid.UUID | None
    movement_type: str
    quantity_delta: int
    reference_type: str | None
    reference_id: str | None
    reason: str
    created_at: datetime

