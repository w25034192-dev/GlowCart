from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.promotions import (
    CouponCreateRequest,
    CouponResponse,
    PromotionCreateRequest,
    PromotionResponse,
)
from app.services.promotion_service import PromotionService

router = APIRouter(tags=["Promotions & Coupons"])


@router.get("/promotions", response_model=list[PromotionResponse])
def list_promotions(db: Session = Depends(get_db)):
    return PromotionService(db).list_promotions(active_only=True)


@router.post("/admin/promotions", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(
    payload: PromotionCreateRequest,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return PromotionService(db).create_promotion(payload, actor)


@router.get("/admin/coupons", response_model=list[CouponResponse])
def list_coupons(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return PromotionService(db).list_coupons()


@router.post("/admin/coupons", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
def create_coupon(
    payload: CouponCreateRequest,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return PromotionService(db).create_coupon(payload, actor)

