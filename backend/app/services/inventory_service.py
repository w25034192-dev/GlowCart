from datetime import date, timedelta
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import (
    Inventory,
    InventoryBatch,
    InventoryMovement,
    ProductVariant,
    User,
)
from app.schemas.inventory import (
    BatchReceiveRequest,
    BatchResponse,
    InventoryAdjustRequest,
    InventoryItemResponse,
    MovementResponse,
)


def format_variant_label(v: ProductVariant) -> str:
    parts = [p for p in [v.shade_name, f"{v.volume_ml}ml" if v.volume_ml else None, v.size] if p]
    return " / ".join(parts) if parts else v.sku


def _as_uuid(value: uuid.UUID | str) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _lock_inventory(self, variant_id: uuid.UUID | str) -> Inventory:
        variant_uuid = _as_uuid(variant_id)
        query = self.db.query(Inventory).filter(Inventory.variant_id == variant_uuid)
        if self.db.bind and self.db.bind.dialect.name != "sqlite":
            query = query.with_for_update()
        inv = query.first()
        if inv is None:
            variant = (
                self.db.query(ProductVariant)
                .filter(ProductVariant.id == variant_uuid)
                .first()
            )
            if variant is None:
                raise NotFoundError("Product variant not found.")
            inv = Inventory(variant_id=variant_uuid, available_quantity=0, reserved_quantity=0)
            self.db.add(inv)
            self.db.flush()
        return inv

    def get_sellable_quantity(self, variant_id: uuid.UUID | str) -> int:
        variant_uuid = _as_uuid(variant_id)
        inv = self.db.query(Inventory).filter(Inventory.variant_id == variant_uuid).first()
        if inv is None:
            return 0
        today = date.today()
        batches = (
            self.db.query(InventoryBatch)
            .filter(
                InventoryBatch.variant_id == variant_uuid,
                InventoryBatch.expiry_date > today,
                InventoryBatch.remaining_quantity > 0,
            )
            .all()
        )
        if batches or (
            self.db.query(InventoryBatch)
            .filter(InventoryBatch.variant_id == variant_uuid)
            .count()
            > 0
        ):
            non_expired_total = sum(b.remaining_quantity for b in batches)
            return max(0, min(inv.available_quantity, non_expired_total - inv.reserved_quantity))
        return max(0, inv.available_quantity)

    def receive_batch(
        self, payload: BatchReceiveRequest, actor: User | None = None
    ) -> BatchResponse:
        variant = (
            self.db.query(ProductVariant)
            .options(joinedload(ProductVariant.product))
            .filter(ProductVariant.id == payload.variant_id)
            .first()
        )
        if variant is None:
            raise NotFoundError("Product variant not found.")
        if payload.expiry_date <= payload.manufacture_date:
            raise BadRequestError("Expiry date must be after manufacture date.")
        existing = (
            self.db.query(InventoryBatch)
            .filter(
                InventoryBatch.variant_id == payload.variant_id,
                InventoryBatch.batch_number == payload.batch_number,
            )
            .first()
        )
        if existing is not None:
            raise ConflictError("Batch number already exists for this variant.")

        batch = InventoryBatch(
            variant_id=payload.variant_id,
            batch_number=payload.batch_number,
            manufacture_date=payload.manufacture_date,
            expiry_date=payload.expiry_date,
            initial_quantity=payload.quantity,
            remaining_quantity=payload.quantity,
            received_date=payload.received_date or date.today(),
        )
        self.db.add(batch)
        self.db.flush()

        inv = self._lock_inventory(payload.variant_id)
        if payload.expiry_date > date.today():
            inv.available_quantity += payload.quantity

        self.db.add(
            InventoryMovement(
                variant_id=payload.variant_id,
                batch_id=batch.id,
                actor_id=actor.id if actor else None,
                movement_type="RECEIVED",
                quantity_delta=payload.quantity,
                reference_type="batch",
                reference_id=batch.batch_number,
                reason=payload.reason,
            )
        )
        self.db.commit()
        self.db.refresh(batch)
        return BatchResponse(
            id=batch.id,
            variant_id=batch.variant_id,
            sku=variant.sku,
            product_name=variant.product.name,
            batch_number=batch.batch_number,
            manufacture_date=batch.manufacture_date,
            expiry_date=batch.expiry_date,
            initial_quantity=batch.initial_quantity,
            remaining_quantity=batch.remaining_quantity,
            received_date=batch.received_date,
            is_expired=batch.expiry_date <= date.today(),
        )

    def adjust_stock(
        self, payload: InventoryAdjustRequest, actor: User | None = None
    ) -> InventoryItemResponse:
        inv = self._lock_inventory(payload.variant_id)
        new_available = inv.available_quantity + payload.quantity_delta
        if new_available < 0:
            raise ConflictError("Stock adjustment rejected: available quantity cannot become negative.")

        inv.available_quantity = new_available
        if payload.low_stock_threshold is not None:
            inv.low_stock_threshold = payload.low_stock_threshold

        # If positive adjustment and no batches changed, or negative adjustment deduct FEFO
        if payload.quantity_delta < 0:
            qty_to_deduct = abs(payload.quantity_delta)
            today = date.today()
            batches = (
                self.db.query(InventoryBatch)
                .filter(
                    InventoryBatch.variant_id == payload.variant_id,
                    InventoryBatch.expiry_date > today,
                    InventoryBatch.remaining_quantity > 0,
                )
                .order_by(InventoryBatch.expiry_date.asc())
                .all()
            )
            for batch in batches:
                if qty_to_deduct == 0:
                    break
                take = min(batch.remaining_quantity, qty_to_deduct)
                batch.remaining_quantity -= take
                qty_to_deduct -= take

        self.db.add(
            InventoryMovement(
                variant_id=payload.variant_id,
                actor_id=actor.id if actor else None,
                movement_type="ADJUSTED",
                quantity_delta=payload.quantity_delta,
                reference_type="manual_adjustment",
                reason=payload.reason,
            )
        )
        self.db.commit()
        return self._serialize_inventory(payload.variant_id)

    def reserve_stock(
        self,
        *,
        variant_id: uuid.UUID,
        quantity: int,
        actor_id: uuid.UUID | None,
        reference_id: str,
    ) -> None:
        if quantity <= 0:
            raise BadRequestError("Reservation quantity must be positive.")
        inv = self._lock_inventory(variant_id)
        sellable = self.get_sellable_quantity(variant_id)
        if sellable < quantity:
            raise ConflictError(
                f"Insufficient non-expired stock for variant {variant_id} (available: {sellable}, requested: {quantity})."
            )
        inv.available_quantity -= quantity
        inv.reserved_quantity += quantity
        self.db.add(
            InventoryMovement(
                variant_id=variant_id,
                actor_id=actor_id,
                movement_type="RESERVED",
                quantity_delta=-quantity,
                reference_type="order",
                reference_id=reference_id,
                reason=f"Reserved for order {reference_id}",
            )
        )

    def release_reserved_stock(
        self,
        *,
        variant_id: uuid.UUID,
        quantity: int,
        actor_id: uuid.UUID | None,
        reference_id: str,
        reason: str = "Order cancelled",
    ) -> None:
        if quantity <= 0:
            return
        inv = self._lock_inventory(variant_id)
        release_qty = min(inv.reserved_quantity, quantity)
        if release_qty <= 0:
            return
        inv.reserved_quantity -= release_qty
        inv.available_quantity += release_qty
        self.db.add(
            InventoryMovement(
                variant_id=variant_id,
                actor_id=actor_id,
                movement_type="RELEASED",
                quantity_delta=release_qty,
                reference_type="order",
                reference_id=reference_id,
                reason=reason,
            )
        )

    def restock_sold_order(
        self,
        *,
        order_number: str,
        actor_id: uuid.UUID | None,
        reason: str = "Order cancelled after FEFO allocation",
    ) -> bool:
        already_returned = (
            self.db.query(InventoryMovement)
            .filter(
                InventoryMovement.reference_type == "order",
                InventoryMovement.reference_id == order_number,
                InventoryMovement.movement_type == "RETURNED",
            )
            .first()
        )
        if already_returned is not None:
            return True

        sold_movements = (
            self.db.query(InventoryMovement)
            .filter(
                InventoryMovement.reference_type == "order",
                InventoryMovement.reference_id == order_number,
                InventoryMovement.movement_type == "SOLD",
            )
            .all()
        )
        if not sold_movements:
            return False

        today = date.today()
        for mov in sold_movements:
            qty = abs(mov.quantity_delta)
            inv = self._lock_inventory(mov.variant_id)
            batch = (
                self.db.query(InventoryBatch)
                .filter(InventoryBatch.id == mov.batch_id)
                .first()
                if mov.batch_id
                else None
            )
            if batch is not None:
                batch.remaining_quantity += qty
            if batch is None or batch.expiry_date > today:
                inv.available_quantity += qty
            self.db.add(
                InventoryMovement(
                    variant_id=mov.variant_id,
                    batch_id=mov.batch_id,
                    actor_id=actor_id,
                    movement_type="RETURNED",
                    quantity_delta=qty,
                    reference_type="order",
                    reference_id=order_number,
                    reason=reason,
                )
            )
        return True

    def allocate_and_deduct_fefo(
        self,
        *,
        variant_id: uuid.UUID | str,
        quantity: int,
        actor_id: uuid.UUID | None,
        reference_type: str,
        reference_id: str,
        from_reserved: bool = False,
    ) -> list[tuple[InventoryBatch, int]]:
        variant_uuid = _as_uuid(variant_id)
        if quantity <= 0:
            raise BadRequestError("Deduction quantity must be positive.")
        inv = self._lock_inventory(variant_uuid)
        today = date.today()
        batch_query = self.db.query(InventoryBatch).filter(
            InventoryBatch.variant_id == variant_uuid,
            InventoryBatch.expiry_date > today,
            InventoryBatch.remaining_quantity > 0,
        )
        if self.db.bind and self.db.bind.dialect.name != "sqlite":
            batch_query = batch_query.with_for_update()
        batches = batch_query.order_by(InventoryBatch.expiry_date.asc()).all()

        total_batch_remaining = sum(b.remaining_quantity for b in batches)
        if total_batch_remaining < quantity:
            raise ConflictError("Insufficient non-expired batch stock for FEFO allocation.")

        if from_reserved:
            if inv.reserved_quantity < quantity:
                raise ConflictError("Reserved stock insufficient for finalization.")
            inv.reserved_quantity -= quantity
        else:
            if inv.available_quantity < quantity:
                raise ConflictError("Available stock insufficient for deduction.")
            inv.available_quantity -= quantity

        remaining = quantity
        allocations: list[tuple[InventoryBatch, int]] = []
        for batch in batches:
            if remaining == 0:
                break
            take = min(batch.remaining_quantity, remaining)
            batch.remaining_quantity -= take
            remaining -= take
            allocations.append((batch, take))
            self.db.add(
                InventoryMovement(
                    variant_id=variant_uuid,
                    batch_id=batch.id,
                    actor_id=actor_id,
                    movement_type="SOLD",
                    quantity_delta=-take,
                    reference_type=reference_type,
                    reference_id=reference_id,
                    reason=f"FEFO deduction from batch {batch.batch_number}",
                )
            )
        return allocations

    def list_inventory(self) -> list[InventoryItemResponse]:
        variants = (
            self.db.query(ProductVariant)
            .options(joinedload(ProductVariant.product), joinedload(ProductVariant.inventory))
            .all()
        )
        items: list[InventoryItemResponse] = []
        for v in variants:
            inv = v.inventory
            avail = inv.available_quantity if inv else 0
            res = inv.reserved_quantity if inv else 0
            thresh = inv.low_stock_threshold if inv else 10
            sellable = self.get_sellable_quantity(v.id)
            items.append(
                InventoryItemResponse(
                    variant_id=v.id,
                    sku=v.sku,
                    product_name=v.product.name,
                    variant_label=format_variant_label(v),
                    available_quantity=avail,
                    reserved_quantity=res,
                    sellable_quantity=sellable,
                    low_stock_threshold=thresh,
                    is_low_stock=0 < sellable <= thresh,
                    is_out_of_stock=sellable == 0,
                    updated_at=inv.updated_at if inv else v.updated_at,
                )
            )
        return items

    def list_low_stock(self) -> list[InventoryItemResponse]:
        return [item for item in self.list_inventory() if item.is_low_stock or item.is_out_of_stock]

    def list_expiring_batches(self, days: int = 60) -> dict:
        today = date.today()
        cutoff = today + timedelta(days=days)
        batches = (
            self.db.query(InventoryBatch)
            .options(joinedload(InventoryBatch.variant).joinedload(ProductVariant.product))
            .filter(InventoryBatch.remaining_quantity > 0, InventoryBatch.expiry_date <= cutoff)
            .order_by(InventoryBatch.expiry_date.asc())
            .all()
        )
        expired: list[BatchResponse] = []
        expiring_soon: list[BatchResponse] = []
        for b in batches:
            item = BatchResponse(
                id=b.id,
                variant_id=b.variant_id,
                sku=b.variant.sku,
                product_name=b.variant.product.name,
                batch_number=b.batch_number,
                manufacture_date=b.manufacture_date,
                expiry_date=b.expiry_date,
                initial_quantity=b.initial_quantity,
                remaining_quantity=b.remaining_quantity,
                received_date=b.received_date,
                is_expired=b.expiry_date <= today,
            )
            if b.expiry_date <= today:
                expired.append(item)
            else:
                expiring_soon.append(item)
        return {"expired": expired, "expiring_soon": expiring_soon}

    def list_movements(self, variant_id: uuid.UUID | None = None, limit: int = 100) -> list[MovementResponse]:
        q = self.db.query(InventoryMovement)
        if variant_id:
            q = q.filter(InventoryMovement.variant_id == variant_id)
        rows = q.order_by(InventoryMovement.created_at.desc()).limit(limit).all()
        return [
            MovementResponse(
                id=m.id,
                variant_id=m.variant_id,
                batch_id=m.batch_id,
                actor_id=m.actor_id,
                movement_type=m.movement_type,
                quantity_delta=m.quantity_delta,
                reference_type=m.reference_type,
                reference_id=m.reference_id,
                reason=m.reason,
                created_at=m.created_at,
            )
            for m in rows
        ]

    def _serialize_inventory(self, variant_id: uuid.UUID) -> InventoryItemResponse:
        v = (
            self.db.query(ProductVariant)
            .options(joinedload(ProductVariant.product), joinedload(ProductVariant.inventory))
            .filter(ProductVariant.id == variant_id)
            .one()
        )
        inv = v.inventory
        avail = inv.available_quantity if inv else 0
        res = inv.reserved_quantity if inv else 0
        thresh = inv.low_stock_threshold if inv else 10
        sellable = self.get_sellable_quantity(v.id)
        return InventoryItemResponse(
            variant_id=v.id,
            sku=v.sku,
            product_name=v.product.name,
            variant_label=format_variant_label(v),
            available_quantity=avail,
            reserved_quantity=res,
            sellable_quantity=sellable,
            low_stock_threshold=thresh,
            is_low_stock=0 < sellable <= thresh,
            is_out_of_stock=sellable == 0,
            updated_at=inv.updated_at if inv else v.updated_at,
        )
