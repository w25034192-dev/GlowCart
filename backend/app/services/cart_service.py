from decimal import Decimal
import uuid
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models import (
    Cart,
    CartItem,
    Product,
    ProductVariant,
    User,
    Wishlist,
    WishlistItem,
)
from app.schemas.cart_wishlist import (
    CartItemResponse,
    CartResponse,
    WishlistItemResponse,
    WishlistResponse,
)
from app.services.inventory_service import InventoryService
from app.services.promotion_service import PromotionService


class CartWishlistService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_or_create_cart(self, user: User) -> Cart:
        cart = self.db.query(Cart).filter(Cart.user_id == user.id).first()
        if cart is None:
            cart = Cart(user_id=user.id)
            self.db.add(cart)
            self.db.flush()
        return cart

    def _get_or_create_wishlist(self, user: User) -> Wishlist:
        wishlist = self.db.query(Wishlist).filter(Wishlist.user_id == user.id).first()
        if wishlist is None:
            wishlist = Wishlist(user_id=user.id)
            self.db.add(wishlist)
            self.db.flush()
        return wishlist

    def get_cart(self, user: User, coupon_code: str | None = None) -> CartResponse:
        cart = self._get_or_create_cart(user)
        self.db.commit()
        items_rows = (
            self.db.query(CartItem)
            .options(
                joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
                .joinedload(Product.brand),
                joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
                .joinedload(Product.images),
            )
            .filter(CartItem.cart_id == cart.id)
            .all()
        )
        inv_service = InventoryService(self.db)
        items: list[CartItemResponse] = []
        subtotal = Decimal("0.00")
        for row in items_rows:
            v = row.variant
            p = v.product
            line_total = (v.price * row.quantity).quantize(Decimal("0.01"))
            subtotal += line_total
            primary_img = next((img.image_url for img in p.images if img.is_primary), None)
            if not primary_img and p.images:
                primary_img = p.images[0].image_url
            items.append(
                CartItemResponse(
                    id=row.id,
                    variant_id=v.id,
                    product_id=p.id,
                    product_name=p.name,
                    brand_name=p.brand.name,
                    sku=v.sku,
                    shade_name=v.shade_name,
                    hex_color=v.hex_color,
                    volume_ml=v.volume_ml,
                    size=v.size,
                    unit_price=v.price,
                    quantity=row.quantity,
                    line_total=line_total,
                    available_quantity=inv_service.get_sellable_quantity(v.id),
                    image_url=primary_img,
                )
            )

        discount = Decimal("0.00")
        coupon_msg: str | None = None
        applied_code: str | None = None
        if coupon_code and subtotal > 0:
            try:
                coupon, discount = PromotionService(self.db).validate_and_compute_discount(
                    coupon_code, subtotal
                )
                applied_code = coupon.code
                coupon_msg = f"Coupon {coupon.code} applied."
            except BadRequestError as exc:
                coupon_msg = str(exc.detail)

        settings = get_settings()
        discounted_subtotal = max(Decimal("0.00"), subtotal - discount)
        shipping = (
            Decimal("0.00")
            if subtotal == 0 or discounted_subtotal >= Decimal(str(settings.free_shipping_threshold))
            else Decimal(str(settings.default_shipping_fee)).quantize(Decimal("0.01"))
        )
        total = (discounted_subtotal + shipping).quantize(Decimal("0.01"))

        return CartResponse(
            id=cart.id,
            items=items,
            subtotal=subtotal.quantize(Decimal("0.01")),
            discount_amount=discount.quantize(Decimal("0.01")),
            shipping_fee=shipping,
            total_amount=total,
            coupon_code=applied_code,
            coupon_message=coupon_msg,
        )

    def add_cart_item(self, user: User, variant_id: uuid.UUID, quantity: int) -> CartResponse:
        variant = (
            self.db.query(ProductVariant)
            .filter(ProductVariant.id == variant_id, ProductVariant.status == "ACTIVE")
            .first()
        )
        if variant is None:
            raise NotFoundError("Product variant not found.")
        cart = self._get_or_create_cart(user)
        existing = (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart.id, CartItem.variant_id == variant_id)
            .first()
        )
        new_qty = (existing.quantity + quantity) if existing else quantity
        sellable = InventoryService(self.db).get_sellable_quantity(variant_id)
        if sellable < new_qty:
            raise ConflictError(
                f"Insufficient non-expired stock (available: {sellable}, requested: {new_qty})."
            )
        if existing:
            existing.quantity = new_qty
        else:
            self.db.add(CartItem(cart_id=cart.id, variant_id=variant_id, quantity=quantity))
        self.db.commit()
        return self.get_cart(user)

    def update_cart_item(self, user: User, item_id: uuid.UUID, quantity: int) -> CartResponse:
        cart = self._get_or_create_cart(user)
        item = (
            self.db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
            .first()
        )
        if item is None:
            raise NotFoundError("Cart item not found.")
        sellable = InventoryService(self.db).get_sellable_quantity(item.variant_id)
        if sellable < quantity:
            raise ConflictError(f"Insufficient stock (available: {sellable}).")
        item.quantity = quantity
        self.db.commit()
        return self.get_cart(user)

    def remove_cart_item(self, user: User, item_id: uuid.UUID) -> CartResponse:
        cart = self._get_or_create_cart(user)
        item = (
            self.db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
            .first()
        )
        if item is None:
            raise NotFoundError("Cart item not found.")
        self.db.delete(item)
        self.db.commit()
        return self.get_cart(user)

    def get_wishlist(self, user: User) -> WishlistResponse:
        wl = self._get_or_create_wishlist(user)
        self.db.commit()
        rows = (
            self.db.query(WishlistItem)
            .options(
                joinedload(WishlistItem.product).joinedload(Product.brand),
                joinedload(WishlistItem.product).joinedload(Product.variants),
                joinedload(WishlistItem.product).joinedload(Product.images),
            )
            .filter(WishlistItem.wishlist_id == wl.id)
            .all()
        )
        items: list[WishlistItemResponse] = []
        for row in rows:
            p = row.product
            prices = [v.price for v in p.variants if v.status == "ACTIVE"]
            primary_img = next((img.image_url for img in p.images if img.is_primary), None)
            if not primary_img and p.images:
                primary_img = p.images[0].image_url
            items.append(
                WishlistItemResponse(
                    id=row.id,
                    product_id=p.id,
                    product_name=p.name,
                    slug=p.slug,
                    brand_name=p.brand.name,
                    min_price=min(prices) if prices else None,
                    primary_image_url=primary_img,
                )
            )
        return WishlistResponse(id=wl.id, items=items)

    def add_wishlist_item(self, user: User, product_id: uuid.UUID) -> WishlistResponse:
        if not self.db.query(Product).filter(Product.id == product_id).first():
            raise NotFoundError("Product not found.")
        wl = self._get_or_create_wishlist(user)
        existing = (
            self.db.query(WishlistItem)
            .filter(WishlistItem.wishlist_id == wl.id, WishlistItem.product_id == product_id)
            .first()
        )
        if existing is None:
            self.db.add(WishlistItem(wishlist_id=wl.id, product_id=product_id))
            self.db.commit()
        return self.get_wishlist(user)

    def remove_wishlist_item(self, user: User, item_or_product_id: uuid.UUID) -> WishlistResponse:
        wl = self._get_or_create_wishlist(user)
        item = (
            self.db.query(WishlistItem)
            .filter(
                WishlistItem.wishlist_id == wl.id,
                (WishlistItem.id == item_or_product_id)
                | (WishlistItem.product_id == item_or_product_id),
            )
            .first()
        )
        if item is None:
            raise NotFoundError("Wishlist item not found.")
        self.db.delete(item)
        self.db.commit()
        return self.get_wishlist(user)

