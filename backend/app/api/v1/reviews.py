import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.engagement import (
    ReviewCreateRequest,
    ReviewModerateRequest,
    ReviewResponse,
    ReviewUpdateRequest,
)
from app.services.engagement_service import EngagementService

router = APIRouter(tags=["Reviews"])


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return EngagementService(db).create_review(user, payload)


@router.get("/products/{product_id}/reviews", response_model=list[ReviewResponse])
def list_product_reviews(product_id: uuid.UUID, db: Session = Depends(get_db)):
    return EngagementService(db).list_product_reviews(product_id)


@router.get("/admin/reviews", response_model=list[ReviewResponse])
def list_all_reviews_admin(
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return EngagementService(db).list_all_reviews_admin()


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: uuid.UUID,
    payload: ReviewUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return EngagementService(db).update_review(review_id, user, payload)


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    EngagementService(db).delete_review(review_id, user)


@router.patch("/admin/reviews/{review_id}/moderate", response_model=ReviewResponse)
def moderate_review(
    review_id: uuid.UUID,
    payload: ReviewModerateRequest,
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return EngagementService(db).moderate_review(review_id, payload.is_approved)

