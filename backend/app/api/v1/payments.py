import uuid
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.config import get_settings
from app.core.rate_limiter import enforce_rate_limit
from app.db.session import get_db
from app.models import User
from app.schemas.payments import (
    PaymentCreateRequest,
    PaymentResponse,
    PaymentWebhookRequest,
    RefundRequest,
)
from app.services.payment_service import PaymentService

router = APIRouter(tags=["Payments"])
settings = get_settings()
payment_rate_limit = enforce_rate_limit("payment", settings.rate_limit_payment_per_minute)


@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(payment_rate_limit)],
)
def initiate_payment(
    payload: PaymentCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PaymentService(db).initiate_payment(user, payload.order_id)


@router.get("/admin/payments", response_model=list[PaymentResponse])
def list_payments_admin(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return PaymentService(db).list_payments_admin()


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PaymentService(db).get_payment(payment_id, user)


@router.post("/payments/webhook", dependencies=[Depends(payment_rate_limit)])
async def payment_webhook(
    request: Request,
    payload: PaymentWebhookRequest,
    x_webhook_signature: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    return PaymentService(db).process_webhook(raw_body, x_webhook_signature, payload)


@router.post("/admin/payments/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: uuid.UUID,
    payload: RefundRequest,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return PaymentService(db).refund_payment_admin(payment_id, actor, payload.reason)

