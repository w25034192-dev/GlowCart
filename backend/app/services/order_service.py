from decimal import Decimal
import threading
import uuid
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, ConflictError, ForbiddenError, NotFoundError
from app.models import (
    Address,
    Cart,
    CartItem,
    CouponUsage,
    InventoryMovement,
    Notification,
    Order,
    OrderItem,
    Payment,
    Product,
    ProductVariant,
    User,
)
from app.schemas.orders import OrderCreateRequest, OrderItemResponse, OrderResponse
from app.services.audit_service import record_audit_log
from app.services.inventory_service import InventoryService, format_variant_label
from app.services.promotion_service import PromotionService

# Process-level mutex protecting variant stock reservation on SQLite during concurrent tests
_CHECKOUT_LOCK = threading.Lock()

ORDER_TRANSITIONS: dict[str, set[str]] = {
    "PENDING": {"PAYMENT_PENDING", "CONFIRMED", "CANCELLED"},
    "PAYMENT_PENDING": {"PAID", "CANCELLED"},
    "PAID": {"CONFIRMED", "PROCESSING", "REFUNDED", "CANCELLED"},
    "CONFIRMED": {"PROCESSING", "SHIPPED", "CANCELLED"},
    "PROCESSING": {"SHIPPED", "CANCELLED"},
    "SHIPPED": {"DELIVERED"},
    "DELIVERED": {"REFUNDED"},
    "CANCELLED": set(),
    "REFUNDED": set(),
}


def serialize_order(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        user_id=order.user_id,
        status=order.status,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        currency=order.currency,
        subtotal=order.subtotal,
        discount_amount=order.discount_amount,
        shipping_fee=order.shipping_fee,
        total_amount=order.total_amount,
        coupon_code=order.coupon_code,
        shipping_address_snapshot=order.shipping_address_snapshot,
        notes=order.notes,
        tracking_number=order.tracking_number,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                variant_id=item.variant_id,
                product_name_snapshot=item.product_name_snapshot,
                brand_name_snapshot=item.brand_name_snapshot,
                category_name_snapshot=item.category_name_snapshot,
                variant_sku_snapshot=item.variant_sku_snapshot,
                variant_label_snapshot=item.variant_label_snapshot,
                shade_name_snapshot=item.shade_name_snapshot,
                volume_ml_snapshot=item.volume_ml_snapshot,
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_total=item.line_total,
            )
            for item in order.items
        ],
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_order(self, user: User, payload: OrderCreateRequest) -> OrderResponse:
        with _CHECKOUT_LOCK:
            if payload.idempotency_key:
                existing = (
                    self.db.query(Order)
                    .options(joinedload(Order.items))
                    .filter(
                        Order.user_id == user.id,
                        Order.idempotency_key == payload.idempotency_key,
                    )
                    .first()
                )
                if existing is not None:
                    return serialize_order(existing)

            address = (
                self.db.query(Address)
                .filter(Address.id == payload.address_id, Address.user_id == user.id)
                .first()
            )
            if address is None:
                raise NotFoundError("Delivery address not found.")

            cart = self.db.query(Cart).filter(Cart.user_id == user.id).first()
            if cart is None:
                raise BadRequestError("Your cart is empty.")
            cart_items = (
                self.db.query(CartItem)
                .options(
                    joinedload(CartItem.variant)
                    .joinedload(ProductVariant.product)
                    .joinedload(Product.brand),
                    joinedload(CartItem.variant)
                    .joinedload(ProductVariant.product)
                    .joinedload(Product.category),
                )
                .filter(CartItem.cart_id == cart.id)
                .all()
            )
            if not cart_items:
                raise BadRequestError("Your cart is empty.")

            inv_service = InventoryService(self.db)
            order_number = f"GC-{uuid.uuid4().hex[:10].upper()}"

            subtotal = Decimal("0.00")
            for ci in cart_items:
                subtotal += (ci.variant.price * ci.quantity).quantize(Decimal("0.01"))

            discount = Decimal("0.00")
            coupon = None
            if payload.coupon_code:
                coupon, discount = PromotionService(self.db).validate_and_compute_discount(
                    payload.coupon_code, subtotal
                )

            settings = get_settings()
            discounted_subtotal = max(Decimal("0.00"), subtotal - discount)
            shipping_fee = (
                Decimal("0.00")
                if discounted_subtotal >= Decimal(str(settings.free_shipping_threshold))
                else Decimal(str(settings.default_shipping_fee)).quantize(Decimal("0.01"))
            )
            total_amount = (discounted_subtotal + shipping_fee).quantize(Decimal("0.01"))

            address_snapshot = {
                "label": address.label,
                "recipient_name": address.recipient_name,
                "phone": address.phone,
                "line1": address.line1,
                "line2": address.line2,
                "city": address.city,
                "state": address.state,
                "postal_code": address.postal_code,
                "country": address.country,
            }

            initial_status = "CONFIRMED" if payload.payment_method == "COD" else "PAYMENT_PENDING"
            order = Order(
                order_number=order_number,
                idempotency_key=payload.idempotency_key,
                user_id=user.id,
                status=initial_status,
                payment_method=payload.payment_method,
                payment_status="UNPAID",
                currency="USD",
                subtotal=subtotal,
                discount_amount=discount,
                shipping_fee=shipping_fee,
                total_amount=total_amount,
                coupon_code=coupon.code if coupon else None,
                shipping_address_snapshot=address_snapshot,
                notes=payload.notes,
            )
            self.db.add(order)
            self.db.flush()

            # Reserve stock atomically and create immutable item snapshots
            for ci in cart_items:
                v = ci.variant
                p = v.product
                inv_service.reserve_stock(
                    variant_id=v.id,
                    quantity=ci.quantity,
                    actor_id=user.id,
                    reference_id=order_number,
                )
                line_total = (v.price * ci.quantity).quantize(Decimal("0.01"))
                self.db.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=p.id,
                        variant_id=v.id,
                        product_name_snapshot=p.name,
                        brand_name_snapshot=p.brand.name if p.brand else None,
                        category_name_snapshot=p.category.name if p.category else None,
                        variant_sku_snapshot=v.sku,
                        variant_label_snapshot=format_variant_label(v),
                        shade_name_snapshot=v.shade_name,
                        volume_ml_snapshot=v.volume_ml,
                        unit_price=v.price,
                        quantity=ci.quantity,
                        line_total=line_total,
                    )
                )

            provider = "COD_ADAPTER" if payload.payment_method == "COD" else "GLOWCART_SANDBOX"
            self.db.add(
                Payment(
                    order_id=order.id,
                    method=payload.payment_method,
                    provider=provider,
                    status="PENDING",
                    amount=total_amount,
                    currency="USD",
                )
            )

            if coupon is not None:
                coupon.used_count += 1
                self.db.add(
                    CouponUsage(
                        coupon_id=coupon.id,
                        user_id=user.id,
                        order_id=order.id,
                        discount_applied=discount,
                    )
                )

            # Clear cart items
            for ci in cart_items:
                self.db.delete(ci)

            self.db.add(
                Notification(
                    user_id=user.id,
                    title=f"Order {order_number} placed",
                    body=(
                        f"Your order {order_number} (${total_amount:.2f}) is {initial_status}."
                    ),
                    category="ORDER",
                )
            )
            record_audit_log(
                self.db,
                actor_id=user.id,
                action="ORDER_CREATED",
                resource_type="order",
                resource_id=str(order.id),
                details={"order_number": order_number, "total": str(total_amount)},
            )
            self.db.commit()
            return self.get_order_by_id(order.id, user=user)

    def list_user_orders(self, user: User) -> list[OrderResponse]:
        orders = (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.user_id == user.id)
            .order_by(Order.created_at.desc())
            .all()
        )
        return [serialize_order(o) for o in orders]

    def list_all_orders(self) -> list[OrderResponse]:
        orders = (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .order_by(Order.created_at.desc())
            .all()
        )
        return [serialize_order(o) for o in orders]

    def get_order_by_id(self, order_id: uuid.UUID, user: User, allow_admin: bool = False) -> OrderResponse:
        order = (
            self.db.query(Order)
            .options(joinedload(Order.items))
            .filter(Order.id == order_id)
            .first()
        )
        if order is None:
            raise NotFoundError("Order not found.")
        role = user.role.name if user.role else "customer"
        if order.user_id != user.id and not (allow_admin and role in {"admin", "super_admin"}):
            raise ForbiddenError("You cannot view this order.")
        return serialize_order(order)

    def finalize_fefo_for_order(self, order: Order, actor_id: uuid.UUID | None) -> None:
        # Check if SOLD movements already exist for this order to ensure idempotency
        already_sold = (
            self.db.query(InventoryMovement)
            .filter(
                InventoryMovement.reference_type == "order",
                InventoryMovement.reference_id == order.order_number,
                InventoryMovement.movement_type == "SOLD",
            )
            .first()
        )
        if already_sold is not None:
            return
        inv_service = InventoryService(self.db)
        for item in order.items:
            if item.variant_id:
                inv_service.allocate_and_deduct_fefo(
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    actor_id=actor_id,
                    reference_type="order",
                    reference_id=order.order_number,
                    from_reserved=True,
                )

    def cancel_order_by_customer(self, order_id: uuid.UUID, user: User) -> OrderResponse:
        order = (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.payment))
            .filter(Order.id == order_id, Order.user_id == user.id)
            .first()
        )
        if order is None:
            raise NotFoundError("Order not found.")
        if order.status not in {"PENDING", "PAYMENT_PENDING", "CONFIRMED"}:
            raise ConflictError("Order can no longer be cancelled at this stage.")

        inv_service = InventoryService(self.db)
        for item in order.items:
            if item.variant_id:
                inv_service.release_reserved_stock(
                    variant_id=item.variant_id,
                    quantity=item.quantity,
                    actor_id=user.id,
                    reference_id=order.order_number,
                    reason="Customer cancelled order",
                )
        order.status = "CANCELLED"
        if order.payment and order.payment.status == "PENDING":
            order.payment.status = "CANCELLED"
        self.db.add(
            Notification(
                user_id=user.id,
                title=f"Order {order.order_number} cancelled",
                body="Your order has been cancelled and reserved stock released.",
                category="ORDER",
            )
        )
        record_audit_log(
            self.db,
            actor_id=user.id,
            action="ORDER_CANCELLED_BY_CUSTOMER",
            resource_type="order",
            resource_id=str(order.id),
        )
        self.db.commit()
        return self.get_order_by_id(order.id, user=user)

    def update_order_status_admin(
        self,
        order_id: uuid.UUID,
        new_status: str,
        actor: User,
        tracking_number: str | None = None,
    ) -> OrderResponse:
        order = (
            self.db.query(Order)
            .options(joinedload(Order.items), joinedload(Order.payment))
            .filter(Order.id == order_id)
            .first()
        )
        if order is None:
            raise NotFoundError("Order not found.")
        if new_status != order.status and new_status not in ORDER_TRANSITIONS.get(order.status, set()):
            raise ConflictError(
                f"Invalid order transition from {order.status} to {new_status}."
            )

        if new_status != order.status:
            if new_status in {"PROCESSING", "SHIPPED", "PAID"}:
                self.finalize_fefo_for_order(order, actor.id)

            if new_status == "DELIVERED" and order.payment_method == "COD":
                self.finalize_fefo_for_order(order, actor.id)
                order.payment_status = "PAID"
                if order.payment:
                    order.payment.status = "PAID"

            if new_status == "CANCELLED":
                inv_service = InventoryService(self.db)
                restocked = inv_service.restock_sold_order(
                    order_number=order.order_number,
                    actor_id=actor.id,
                    reason="Admin cancelled finalized order",
                )
                if not restocked:
                    for item in order.items:
                        if item.variant_id:
                            inv_service.release_reserved_stock(
                                variant_id=item.variant_id,
                                quantity=item.quantity,
                                actor_id=actor.id,
                                reference_id=order.order_number,
                                reason="Admin cancelled order",
                            )

            order.status = new_status
        if tracking_number is not None:
            order.tracking_number = tracking_number

        self.db.add(
            Notification(
                user_id=order.user_id,
                title=f"Order {order.order_number} updated",
                body=f"Your order status is now {new_status}.",
                category="ORDER",
            )
        )
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="ORDER_STATUS_UPDATED",
            resource_type="order",
            resource_id=str(order.id),
            details={"new_status": new_status, "tracking_number": tracking_number},
        )
        self.db.commit()
        return self.get_order_by_id(order.id, user=actor, allow_admin=True)

