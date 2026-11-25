import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.orders import OrderCreateRequest, OrderResponse, OrderStatusUpdateRequest
from app.services.order_service import OrderService

router = APIRouter(tags=["Orders"])


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).create_order(user, payload)


@router.get("/orders", response_model=list[OrderResponse])
def list_my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return OrderService(db).list_user_orders(user)


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).get_order_by_id(order_id, user=user, allow_admin=True)


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_my_order(
    order_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return OrderService(db).cancel_order_by_customer(order_id, user)


@router.get("/admin/orders", response_model=list[OrderResponse])
def list_all_orders(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return OrderService(db).list_all_orders()


@router.patch("/admin/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: uuid.UUID,
    payload: OrderStatusUpdateRequest,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return OrderService(db).update_order_status_admin(
        order_id, payload.status, actor=actor, tracking_number=payload.tracking_number
    )

