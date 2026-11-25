from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field


class PromotionCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    description: str | None = None
    discount_type: str = Field(pattern="^(PERCENTAGE|FIXED)$")
    discount_value: Decimal = Field(gt=0)
    banner_image_url: str | None = None
    starts_at: datetime
    ends_at: datetime
    is_active: bool = True
    coupon_code: str | None = Field(default=None, min_length=3, max_length=60)
    min_order_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    max_uses: int | None = Field(default=None, ge=1)


class CouponCreateRequest(BaseModel):
    promotion_id: uuid.UUID | None = None
    code: str = Field(min_length=3, max_length=60)
    discount_type: str = Field(pattern="^(PERCENTAGE|FIXED)$")
    discount_value: Decimal = Field(gt=0)
    min_order_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    max_uses: int | None = Field(default=None, ge=1)
    expires_at: datetime | None = None
    is_active: bool = True


class CouponResponse(BaseModel):
    id: uuid.UUID
    promotion_id: uuid.UUID | None
    code: str
    discount_type: str
    discount_value: Decimal
    min_order_amount: Decimal
    max_uses: int | None
    used_count: int
    expires_at: datetime | None
    is_active: bool


class PromotionResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    discount_type: str
    discount_value: Decimal
    banner_image_url: str | None
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    coupons: list[CouponResponse] = Field(default_factory=list)

