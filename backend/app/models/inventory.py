from datetime import date, datetime, timezone
import uuid
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, new_uuid


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("available_quantity >= 0", name="ck_inventory_available_non_neg"),
        CheckConstraint("reserved_quantity >= 0", name="ck_inventory_reserved_non_neg"),
        CheckConstraint("low_stock_threshold >= 0", name="ck_inventory_threshold_non_neg"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    available_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    variant: Mapped["ProductVariant"] = relationship(back_populates="inventory")


class InventoryBatch(Base, TimestampMixin):
    __tablename__ = "inventory_batches"
    __table_args__ = (
        UniqueConstraint("variant_id", "batch_number", name="uq_variant_batch_number"),
        CheckConstraint("initial_quantity >= 0", name="ck_batch_initial_non_neg"),
        CheckConstraint("remaining_quantity >= 0", name="ck_batch_remaining_non_neg"),
        Index("ix_batches_variant_expiry", "variant_id", "expiry_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacture_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    initial_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    received_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    variant: Mapped["ProductVariant"] = relationship(back_populates="batches")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (Index("ix_movements_variant_created", "variant_id", "created_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=new_uuid)
    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("inventory_batches.id", ondelete="SET NULL"), nullable=True
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    quantity_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    variant: Mapped["ProductVariant"] = relationship(back_populates="movements")

