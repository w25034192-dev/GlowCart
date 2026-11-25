from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    address_id: uuid.UUID
    payment_method: str = Field(pattern="^(COD|SANDBOX)$")
    coupon_code: str | None = None
    idempotency_key: str | None = Field(default=None, max_length=128)
    notes: str | None = Field(default=None, max_length=500)


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(
        pattern="^(PENDING|PAYMENT_PENDING|PAID|CONFIRMED|PROCESSING|SHIPPED|DELIVERED|CANCELLED|REFUNDED)$"
    )
    tracking_number: str | None = Field(default=None, max_length=100)


class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID | None
    variant_id: uuid.UUID | None
    product_name_snapshot: str
    brand_name_snapshot: str | None
    category_name_snapshot: str | None
    variant_sku_snapshot: str
    variant_label_snapshot: str
    shade_name_snapshot: str | None
    volume_ml_snapshot: int | None
    unit_price: Decimal
    quantity: int
    line_total: Decimal


class OrderResponse(BaseModel):
    id: uuid.UUID
    order_number: str
    user_id: uuid.UUID
    status: str
    payment_method: str
    payment_status: str
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    shipping_fee: Decimal
    total_amount: Decimal
    coupon_code: str | None
    shipping_address_snapshot: dict
    notes: str | None
    tracking_number: str | None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

