from datetime import datetime
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=140)
    description: str | None = None
    parent_id: uuid.UUID | None = None
    image_url: str | None = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    parent_id: uuid.UUID | None = None
    image_url: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    parent_id: uuid.UUID | None
    name: str
    slug: str
    description: str | None
    image_url: str | None
    is_active: bool
    sort_order: int


class BrandCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=140)
    description: str | None = None
    country_of_origin: str | None = None
    logo_url: str | None = None
    is_featured: bool = False


class BrandUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    country_of_origin: str | None = None
    logo_url: str | None = None
    is_featured: bool | None = None
    is_active: bool | None = None


class BrandResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    country_of_origin: str | None
    logo_url: str | None
    is_featured: bool
    is_active: bool


class ProductImageResponse(BaseModel):
    id: uuid.UUID
    image_url: str
    alt_text: str | None
    is_primary: bool
    sort_order: int


class VariantCreate(BaseModel):
    product_id: uuid.UUID
    sku: str = Field(min_length=2, max_length=100)
    shade_name: str | None = None
    shade_code: str | None = None
    color_name: str | None = None
    hex_color: str | None = None
    volume_ml: int | None = Field(default=None, gt=0)
    weight_g: Decimal | None = Field(default=None, gt=0)
    size: str | None = None
    price: Decimal = Field(gt=0)
    original_price: Decimal | None = Field(default=None, gt=0)
    is_available: bool = True
    status: str = "ACTIVE"


class VariantUpdate(BaseModel):
    shade_name: str | None = None
    shade_code: str | None = None
    color_name: str | None = None
    hex_color: str | None = None
    volume_ml: int | None = Field(default=None, gt=0)
    weight_g: Decimal | None = Field(default=None, gt=0)
    size: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    original_price: Decimal | None = Field(default=None, gt=0)
    is_available: bool | None = None
    status: str | None = None


class VariantResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    shade_name: str | None
    shade_code: str | None
    color_name: str | None
    hex_color: str | None
    volume_ml: int | None
    weight_g: Decimal | None
    size: str | None
    price: Decimal
    original_price: Decimal | None
    is_available: bool
    status: str
    available_quantity: int = 0


class ProductCreate(BaseModel):
    category_id: uuid.UUID
    brand_id: uuid.UUID
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=220)
    short_description: str | None = None
    description: str = Field(min_length=3)
    skin_types: list[str] = Field(default_factory=list)
    specifications: dict = Field(default_factory=dict)
    verified_ingredients: str | None = None
    is_featured: bool = False
    is_new_arrival: bool = False
    is_best_seller: bool = False
    is_demo: bool = True


class ProductUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=200)
    short_description: str | None = None
    description: str | None = None
    skin_types: list[str] | None = None
    specifications: dict | None = None
    verified_ingredients: str | None = None
    is_featured: bool | None = None
    is_new_arrival: bool | None = None
    is_best_seller: bool | None = None
    is_active: bool | None = None
    is_archived: bool | None = None


class ProductSummaryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    short_description: str | None
    category_id: uuid.UUID
    category_name: str
    brand_id: uuid.UUID
    brand_name: str
    min_price: Decimal | None
    max_price: Decimal | None
    original_price: Decimal | None
    primary_image_url: str | None
    average_rating: float
    review_count: int
    in_stock: bool
    is_featured: bool
    is_new_arrival: bool
    is_best_seller: bool
    is_demo: bool
    skin_types: list[str]


class ProductDetailResponse(ProductSummaryResponse):
    description: str
    specifications: dict
    verified_ingredients: str | None
    images: list[ProductImageResponse]
    variants: list[VariantResponse]
    created_at: datetime


class PaginatedProductsResponse(BaseModel):
    items: list[ProductSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

