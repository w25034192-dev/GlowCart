from datetime import datetime, timezone
from decimal import Decimal
import uuid
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import Coupon, Promotion, User
from app.schemas.promotions import (
    CouponCreateRequest,
    CouponResponse,
    PromotionCreateRequest,
    PromotionResponse,
)
from app.services.audit_service import record_audit_log


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class PromotionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_promotions(self, active_only: bool = True) -> list[PromotionResponse]:
        q = self.db.query(Promotion)
        if active_only:
            q = q.filter(Promotion.is_active.is_(True))
        promos = q.order_by(Promotion.starts_at.desc()).all()
        coupons = self.db.query(Coupon).all()
        by_promo: dict[uuid.UUID | None, list[CouponResponse]] = {}
        for c in coupons:
            by_promo.setdefault(c.promotion_id, []).append(
                CouponResponse(
                    id=c.id,
                    promotion_id=c.promotion_id,
                    code=c.code,
                    discount_type=c.discount_type,
                    discount_value=c.discount_value,
                    min_order_amount=c.min_order_amount,
                    max_uses=c.max_uses,
                    used_count=c.used_count,
                    expires_at=c.expires_at,
                    is_active=c.is_active,
                )
            )
        return [
            PromotionResponse(
                id=p.id,
                title=p.title,
                description=p.description,
                discount_type=p.discount_type,
                discount_value=p.discount_value,
                banner_image_url=p.banner_image_url,
                starts_at=p.starts_at,
                ends_at=p.ends_at,
                is_active=p.is_active,
                coupons=by_promo.get(p.id, []),
            )
            for p in promos
        ]

    def create_promotion(
        self, payload: PromotionCreateRequest, actor: User
    ) -> PromotionResponse:
        if payload.ends_at <= payload.starts_at:
            raise BadRequestError("Promotion end time must be after start time.")
        if payload.discount_type == "PERCENTAGE" and payload.discount_value > Decimal("90"):
            raise BadRequestError("Percentage discount cannot exceed 90%.")
        promo = Promotion(
            title=payload.title,
            description=payload.description,
            discount_type=payload.discount_type,
            discount_value=payload.discount_value,
            banner_image_url=payload.banner_image_url,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            is_active=payload.is_active,
        )
        self.db.add(promo)
        self.db.flush()

        created_coupons: list[CouponResponse] = []
        if payload.coupon_code:
            code = payload.coupon_code.strip().upper()
            if self.db.query(Coupon).filter(Coupon.code == code).first():
                raise ConflictError("Coupon code already exists.")
            c = Coupon(
                promotion_id=promo.id,
                code=code,
                discount_type=payload.discount_type,
                discount_value=payload.discount_value,
                min_order_amount=payload.min_order_amount,
                max_uses=payload.max_uses,
                expires_at=payload.ends_at,
                is_active=payload.is_active,
            )
            self.db.add(c)
            self.db.flush()
            created_coupons.append(
                CouponResponse(
                    id=c.id,
                    promotion_id=c.promotion_id,
                    code=c.code,
                    discount_type=c.discount_type,
                    discount_value=c.discount_value,
                    min_order_amount=c.min_order_amount,
                    max_uses=c.max_uses,
                    used_count=c.used_count,
                    expires_at=c.expires_at,
                    is_active=c.is_active,
                )
            )
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="PROMOTION_CREATED",
            resource_type="promotion",
            resource_id=str(promo.id),
        )
        self.db.commit()
        self.db.refresh(promo)
        return PromotionResponse(
            id=promo.id,
            title=promo.title,
            description=promo.description,
            discount_type=promo.discount_type,
            discount_value=promo.discount_value,
            banner_image_url=promo.banner_image_url,
            starts_at=promo.starts_at,
            ends_at=promo.ends_at,
            is_active=promo.is_active,
            coupons=created_coupons,
        )

    def create_coupon(self, payload: CouponCreateRequest, actor: User) -> Coupon:
        code = payload.code.strip().upper()
        if self.db.query(Coupon).filter(Coupon.code == code).first():
            raise ConflictError("Coupon code already exists.")
        coupon = Coupon(
            promotion_id=payload.promotion_id,
            code=code,
            discount_type=payload.discount_type,
            discount_value=payload.discount_value,
            min_order_amount=payload.min_order_amount,
            max_uses=payload.max_uses,
            expires_at=payload.expires_at,
            is_active=payload.is_active,
        )
        self.db.add(coupon)
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="COUPON_CREATED",
            resource_type="coupon",
            details={"code": code},
        )
        self.db.commit()
        self.db.refresh(coupon)
        return coupon

    def list_coupons(self) -> list[Coupon]:
        return self.db.query(Coupon).order_by(Coupon.created_at.desc()).all()

    def validate_and_compute_discount(
        self, code: str, subtotal: Decimal
    ) -> tuple[Coupon, Decimal]:
        normalized = code.strip().upper()
        coupon = self.db.query(Coupon).filter(Coupon.code == normalized).first()
        if coupon is None or not coupon.is_active:
            raise BadRequestError("Coupon code is invalid or inactive.")
        if coupon.expires_at and _to_utc(coupon.expires_at) < datetime.now(timezone.utc):
            raise BadRequestError("Coupon code has expired.")
        if coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
            raise BadRequestError("Coupon redemption limit reached.")
        if subtotal < coupon.min_order_amount:
            raise BadRequestError(
                f"Minimum order amount of ${coupon.min_order_amount:.2f} required for this coupon."
            )

        if coupon.discount_type == "PERCENTAGE":
            discount = (subtotal * coupon.discount_value / Decimal("100")).quantize(
                Decimal("0.01")
            )
        else:
            discount = min(subtotal, coupon.discount_value).quantize(Decimal("0.01"))
        return coupon, min(subtotal, discount)

