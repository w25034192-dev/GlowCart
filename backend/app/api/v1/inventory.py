import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.inventory import (
    BatchReceiveRequest,
    BatchResponse,
    InventoryAdjustRequest,
    InventoryItemResponse,
    MovementResponse,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/admin/inventory", tags=["Inventory & Batches"])


@router.get("", response_model=list[InventoryItemResponse])
def list_inventory(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_inventory()


@router.post("/adjustments", response_model=InventoryItemResponse)
def adjust_inventory(
    payload: InventoryAdjustRequest,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return InventoryService(db).adjust_stock(payload, actor=actor)


@router.post("/batches", response_model=BatchResponse, status_code=status.HTTP_201_CREATED)
def receive_batch(
    payload: BatchReceiveRequest,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return InventoryService(db).receive_batch(payload, actor=actor)


@router.get("/low-stock", response_model=list[InventoryItemResponse])
def get_low_stock(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_low_stock()


@router.get("/expiring")
def get_expiring_batches(
    days: int = Query(60, ge=1, le=365),
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_expiring_batches(days=days)


@router.get("/movements", response_model=list[MovementResponse])
def get_inventory_movements(
    variant_id: uuid.UUID | None = None,
    limit: int = Query(100, ge=1, le=500),
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return InventoryService(db).list_movements(variant_id=variant_id, limit=limit)

