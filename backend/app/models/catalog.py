from decimal import Decimal
import uuid
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, new_uuid


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent: Mapped["Category | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Brand(Base, TimestampMixin):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    products: Mapped[list["Product"]] = relationship(back_populates="brand")


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_cat_brand_active", "category_id", "brand_id", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False, index=True)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skin_types: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    specifications: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    verified_ingredients: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_new_arrival: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_best_seller: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="products")
    brand: Mapped["Brand"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )
    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")


class ProductImage(Base, TimestampMixin):
    __tablename__ = "product_images"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_url: Mapped[str] = mapped_column(String(600), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="images")


class ProductVariant(Base, TimestampMixin):
    __tablename__ = "product_variants"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_variant_price_positive"),
        CheckConstraint("original_price IS NULL OR original_price >= price", name="ck_variant_orig_price"),
        Index("ix_variants_product_status", "product_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    shade_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shade_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    color_name: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    hex_color: Mapped[str | None] = mapped_column(String(16), nullable=True)
    volume_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_g: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    size: Mapped[str | None] = mapped_column(String(60), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE", nullable=False)

    product: Mapped["Product"] = relationship(back_populates="variants")
    inventory: Mapped["Inventory | None"] = relationship(
        back_populates="variant", uselist=False, cascade="all, delete-orphan"
    )
    batches: Mapped[list["InventoryBatch"]] = relationship(
        back_populates="variant", cascade="all, delete-orphan"
    )
    movements: Mapped[list["InventoryMovement"]] = relationship(back_populates="variant")

