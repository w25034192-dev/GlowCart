from decimal import Decimal
import uuid
from pydantic import BaseModel, Field


class CartItemAddRequest(BaseModel):
    variant_id: uuid.UUID
    quantity: int = Field(default=1, ge=1, le=50)


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(ge=1, le=50)


class CartItemResponse(BaseModel):
    id: uuid.UUID
    variant_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    brand_name: str
    sku: str
    shade_name: str | None
    hex_color: str | None
    volume_ml: int | None
    size: str | None
    unit_price: Decimal
    quantity: int
    line_total: Decimal
    available_quantity: int
    image_url: str | None


class CartResponse(BaseModel):
    id: uuid.UUID
    items: list[CartItemResponse]
    subtotal: Decimal
    discount_amount: Decimal
    shipping_fee: Decimal
    total_amount: Decimal
    coupon_code: str | None = None
    coupon_message: str | None = None


class WishlistItemAddRequest(BaseModel):
    product_id: uuid.UUID


class WishlistItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    slug: str
    brand_name: str
    min_price: Decimal | None
    primary_image_url: str | None


class WishlistResponse(BaseModel):
    id: uuid.UUID
    items: list[WishlistItemResponse]

