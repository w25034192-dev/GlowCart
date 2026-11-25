from decimal import Decimal
import uuid
from sqlalchemy import (
    JSON,
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


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_order_subtotal_non_neg"),
        CheckConstraint("discount_amount >= 0", name="ck_order_discount_non_neg"),
        CheckConstraint("shipping_fee >= 0", name="ck_order_shipping_non_neg"),
        CheckConstraint("total_amount >= 0", name="ck_order_total_non_neg"),
        Index("ix_orders_user_status", "user_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    order_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(128), unique=True, nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(30), default="UNPAID", nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    shipping_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    coupon_code: Mapped[str | None] = mapped_column(String(60), nullable=True)
    shipping_address_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    payment: Mapped["Payment | None"] = relationship(
        back_populates="order", uselist=False, cascade="all, delete-orphan"
    )


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_qty_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_item_price_non_neg"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    variant_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True
    )
    product_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    brand_name_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category_name_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    variant_sku_snapshot: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_label_snapshot: Mapped[str] = mapped_column(String(160), nullable=False)
    shade_name_snapshot: Mapped[str | None] = mapped_column(String(120), nullable=True)
    volume_ml_snapshot: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (CheckConstraint("amount >= 0", name="ck_payment_amount_non_neg"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    method: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_reference: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    order: Mapped["Order"] = relationship(back_populates="payment")
    transactions: Mapped[list["PaymentTransaction"]] = relationship(
        back_populates="payment", cascade="all, delete-orphan"
    )


class PaymentTransaction(Base, TimestampMixin):
    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    payment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider_event_id: Mapped[str] = mapped_column(
        String(140), unique=True, nullable=False, index=True
    )
    transaction_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    payment: Mapped["Payment"] = relationship(back_populates="transactions")

