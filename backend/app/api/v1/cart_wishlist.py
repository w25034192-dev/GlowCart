import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.cart_wishlist import (
    CartItemAddRequest,
    CartItemUpdateRequest,
    CartResponse,
    WishlistItemAddRequest,
    WishlistResponse,
)
from app.services.cart_service import CartWishlistService

router = APIRouter(tags=["Cart & Wishlist"])


@router.get("/cart", response_model=CartResponse)
def get_cart(
    coupon_code: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CartWishlistService(db).get_cart(user, coupon_code=coupon_code)


@router.post("/cart/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_cart_item(
    payload: CartItemAddRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CartWishlistService(db).add_cart_item(user, payload.variant_id, payload.quantity)


@router.put("/cart/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: uuid.UUID,
    payload: CartItemUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CartWishlistService(db).update_cart_item(user, item_id, payload.quantity)


@router.delete("/cart/items/{item_id}", response_model=CartResponse)
def delete_cart_item(
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CartWishlistService(db).remove_cart_item(user, item_id)


@router.get("/wishlist", response_model=WishlistResponse)
def get_wishlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return CartWishlistService(db).get_wishlist(user)


@router.post("/wishlist/items", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
def add_wishlist_item(
    payload: WishlistItemAddRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CartWishlistService(db).add_wishlist_item(user, payload.product_id)


@router.delete("/wishlist/items/{item_id}", response_model=WishlistResponse)
def delete_wishlist_item(
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CartWishlistService(db).remove_wishlist_item(user, item_id)

