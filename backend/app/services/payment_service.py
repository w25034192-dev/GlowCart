import uuid
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import verify_webhook_signature
from app.models import Notification, Order, Payment, PaymentTransaction, User
from app.schemas.payments import (
    PaymentResponse,
    PaymentTransactionResponse,
    PaymentWebhookRequest,
)
from app.services.audit_service import record_audit_log
from app.services.order_service import OrderService


def serialize_payment(payment: Payment) -> PaymentResponse:
    sandbox_url = (
        f"/checkout/sandbox-pay/{payment.id}" if payment.method == "SANDBOX" else None
    )
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        method=payment.method,
        provider=payment.provider,
        provider_reference=payment.provider_reference,
        status=payment.status,
        amount=payment.amount,
        currency=payment.currency,
        sandbox_checkout_url=sandbox_url,
        transactions=[
            PaymentTransactionResponse(
                id=t.id,
                provider_event_id=t.provider_event_id,
                transaction_type=t.transaction_type,
                status=t.status,
                amount=t.amount,
                created_at=t.created_at,
            )
            for t in payment.transactions
        ],
        created_at=payment.created_at,
    )


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def initiate_payment(self, user: User, order_id: uuid.UUID) -> PaymentResponse:
        order = (
            self.db.query(Order)
            .options(joinedload(Order.payment).joinedload(Payment.transactions))
            .filter(Order.id == order_id, Order.user_id == user.id)
            .first()
        )
        if order is None:
            raise NotFoundError("Order not found.")
        payment = order.payment
        if payment is None:
            payment = Payment(
                order_id=order.id,
                method=order.payment_method,
                provider="GLOWCART_SANDBOX" if order.payment_method == "SANDBOX" else "COD_ADAPTER",
                status="PENDING",
                amount=order.total_amount,
                currency=order.currency,
            )
            self.db.add(payment)
            self.db.flush()

        if not payment.provider_reference:
            payment.provider_reference = f"SBX-{uuid.uuid4().hex[:12].upper()}"
            self.db.commit()
            self.db.refresh(payment)
        return serialize_payment(payment)

    def get_payment(self, payment_id: uuid.UUID, user: User) -> PaymentResponse:
        payment = (
            self.db.query(Payment)
            .options(joinedload(Payment.transactions), joinedload(Payment.order))
            .filter(Payment.id == payment_id)
            .first()
        )
        if payment is None:
            raise NotFoundError("Payment not found.")
        role = user.role.name if user.role else "customer"
        if payment.order.user_id != user.id and role not in {"admin", "super_admin"}:
            raise ForbiddenError("You cannot access this payment record.")
        return serialize_payment(payment)

    def list_payments_admin(self) -> list[PaymentResponse]:
        payments = (
            self.db.query(Payment)
            .options(joinedload(Payment.transactions))
            .order_by(Payment.created_at.desc())
            .all()
        )
        return [serialize_payment(p) for p in payments]

    def process_webhook(
        self, raw_body: bytes, signature: str | None, payload: PaymentWebhookRequest
    ) -> dict:
        settings = get_settings()
        if not signature or not verify_webhook_signature(
            raw_body, signature, settings.payment_webhook_secret
        ):
            raise UnauthorizedError("Invalid payment webhook signature.")

        existing_tx = (
            self.db.query(PaymentTransaction)
            .filter(PaymentTransaction.provider_event_id == payload.provider_event_id)
            .first()
        )
        payment = (
            self.db.query(Payment)
            .options(joinedload(Payment.order).joinedload(Order.items))
            .filter(Payment.id == payload.payment_id)
            .first()
        )
        if payment is None:
            raise NotFoundError("Payment not found.")

        if existing_tx is not None:
            return {
                "payment_id": str(payment.id),
                "status": payment.status,
                "duplicate": True,
            }

        self.db.add(
            PaymentTransaction(
                payment_id=payment.id,
                provider_event_id=payload.provider_event_id,
                transaction_type="WEBHOOK_CAPTURE",
                status=payload.status,
                amount=payment.amount,
                raw_payload=payload.model_dump(mode="json"),
            )
        )

        if payload.status == "PAID":
            payment.status = "PAID"
            payment.order.payment_status = "PAID"
            if payment.order.status in {"PENDING", "PAYMENT_PENDING"}:
                payment.order.status = "PAID"
            OrderService(self.db).finalize_fefo_for_order(payment.order, actor_id=None)
            self.db.add(
                Notification(
                    user_id=payment.order.user_id,
                    title=f"Payment received for {payment.order.order_number}",
                    body=f"Payment of ${payment.amount:.2f} has been verified.",
                    category="PAYMENT",
                )
            )
        else:
            payment.status = "FAILED"
            payment.order.payment_status = "FAILED"

        self.db.commit()
        return {"payment_id": str(payment.id), "status": payment.status, "duplicate": False}

    def refund_payment_admin(
        self, payment_id: uuid.UUID, actor: User, reason: str
    ) -> PaymentResponse:
        payment = (
            self.db.query(Payment)
            .options(joinedload(Payment.order), joinedload(Payment.transactions))
            .filter(Payment.id == payment_id)
            .first()
        )
        if payment is None:
            raise NotFoundError("Payment not found.")
        if payment.status != "PAID":
            raise ConflictError("Only PAID payments can be refunded.")

        payment.status = "REFUNDED"
        payment.order.payment_status = "REFUNDED"
        payment.order.status = "REFUNDED"
        self.db.add(
            PaymentTransaction(
                payment_id=payment.id,
                provider_event_id=f"refund_{uuid.uuid4().hex[:16]}",
                transaction_type="REFUND",
                status="REFUNDED",
                amount=payment.amount,
                raw_payload={"reason": reason, "actor_id": str(actor.id)},
            )
        )
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="PAYMENT_REFUNDED",
            resource_type="payment",
            resource_id=str(payment.id),
            details={"reason": reason, "order_id": str(payment.order_id)},
        )
        self.db.commit()
        self.db.refresh(payment)
        return serialize_payment(payment)

