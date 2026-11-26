from decimal import Decimal
import math
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ConflictError, NotFoundError
from app.models import (
    Brand,
    Category,
    Inventory,
    Product,
    ProductImage,
    ProductVariant,
    Review,
    User,
)
from app.schemas.catalog import (
    BrandCreate,
    BrandUpdate,
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductDetailResponse,
    ProductImageResponse,
    ProductSummaryResponse,
    ProductUpdate,
    VariantCreate,
    VariantResponse,
    VariantUpdate,
)
from app.services.audit_service import record_audit_log
from app.services.inventory_service import InventoryService


def _variant_stock_map(db: Session, variant_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not variant_ids:
        return {}
    inv_service = InventoryService(db)
    return {vid: inv_service.get_sellable_quantity(vid) for vid in variant_ids}


class CatalogService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_categories(self) -> list[Category]:
        return (
            self.db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.sort_order.asc(), Category.name.asc())
            .all()
        )

    def create_category(self, payload: CategoryCreate, actor: User) -> Category:
        if self.db.query(Category).filter(Category.slug == payload.slug).first():
            raise ConflictError("Category slug already exists.")
        cat = Category(**payload.model_dump())
        self.db.add(cat)
        self.db.flush()
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="CATEGORY_CREATED",
            resource_type="category",
            resource_id=str(cat.id),
            details={"name": cat.name},
        )
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def update_category(
        self, category_id: uuid.UUID, payload: CategoryUpdate, actor: User
    ) -> Category:
        cat = self.db.query(Category).filter(Category.id == category_id).first()
        if cat is None:
            raise NotFoundError("Category not found.")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(cat, k, v)
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="CATEGORY_UPDATED",
            resource_type="category",
            resource_id=str(cat.id),
        )
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def list_brands(self) -> list[Brand]:
        return (
            self.db.query(Brand)
            .filter(Brand.is_active.is_(True))
            .order_by(Brand.is_featured.desc(), Brand.name.asc())
            .all()
        )

    def create_brand(self, payload: BrandCreate, actor: User) -> Brand:
        if self.db.query(Brand).filter(Brand.slug == payload.slug).first():
            raise ConflictError("Brand slug already exists.")
        brand = Brand(**payload.model_dump())
        self.db.add(brand)
        self.db.flush()
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="BRAND_CREATED",
            resource_type="brand",
            resource_id=str(brand.id),
            details={"name": brand.name},
        )
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def update_brand(self, brand_id: uuid.UUID, payload: BrandUpdate, actor: User) -> Brand:
        brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
        if brand is None:
            raise NotFoundError("Brand not found.")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(brand, k, v)
        self.db.commit()
        self.db.refresh(brand)
        return brand

    def create_product(self, payload: ProductCreate, actor: User) -> Product:
        if self.db.query(Product).filter(Product.slug == payload.slug).first():
            raise ConflictError("Product slug already exists.")
        if not self.db.query(Category).filter(Category.id == payload.category_id).first():
            raise NotFoundError("Category not found.")
        if not self.db.query(Brand).filter(Brand.id == payload.brand_id).first():
            raise NotFoundError("Brand not found.")

        product = Product(**payload.model_dump())
        self.db.add(product)
        self.db.flush()
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="PRODUCT_CREATED",
            resource_type="product",
            resource_id=str(product.id),
            details={"name": product.name},
        )
        self.db.commit()
        self.db.refresh(product)
        return product

    def update_product(
        self, product_id: uuid.UUID, payload: ProductUpdate, actor: User
    ) -> Product:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            raise NotFoundError("Product not found.")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(product, k, v)
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="PRODUCT_UPDATED",
            resource_type="product",
            resource_id=str(product.id),
        )
        self.db.commit()
        self.db.refresh(product)
        return product

    def archive_product(self, product_id: uuid.UUID, actor: User) -> None:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            raise NotFoundError("Product not found.")
        product.is_active = False
        product.is_archived = True
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="PRODUCT_ARCHIVED",
            resource_type="product",
            resource_id=str(product.id),
        )
        self.db.commit()

    def create_variant(self, payload: VariantCreate, actor: User) -> VariantResponse:
        if not self.db.query(Product).filter(Product.id == payload.product_id).first():
            raise NotFoundError("Product not found.")
        if self.db.query(ProductVariant).filter(ProductVariant.sku == payload.sku).first():
            raise ConflictError("Variant SKU already exists.")
        variant = ProductVariant(**payload.model_dump())
        self.db.add(variant)
        self.db.flush()
        self.db.add(Inventory(variant_id=variant.id, available_quantity=0, reserved_quantity=0))
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="VARIANT_CREATED",
            resource_type="product_variant",
            resource_id=str(variant.id),
            details={"sku": variant.sku},
        )
        self.db.commit()
        self.db.refresh(variant)
        return self._serialize_variant(variant, 0)

    def update_variant(
        self, variant_id: uuid.UUID, payload: VariantUpdate, actor: User
    ) -> VariantResponse:
        variant = self.db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if variant is None:
            raise NotFoundError("Variant not found.")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(variant, k, v)
        record_audit_log(
            self.db,
            actor_id=actor.id,
            action="VARIANT_UPDATED",
            resource_type="product_variant",
            resource_id=str(variant.id),
        )
        self.db.commit()
        self.db.refresh(variant)
        qty = InventoryService(self.db).get_sellable_quantity(variant.id)
        return self._serialize_variant(variant, qty)

    def add_product_image(
        self,
        product_id: uuid.UUID,
        image_url: str,
        alt_text: str | None = None,
        is_primary: bool = False,
    ) -> ProductImage:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            raise NotFoundError("Product not found.")
        if is_primary:
            for img in product.images:
                img.is_primary = False
        img = ProductImage(
            product_id=product.id,
            image_url=image_url,
            alt_text=alt_text or product.name,
            is_primary=is_primary or len(product.images) == 0,
            sort_order=len(product.images),
        )
        self.db.add(img)
        self.db.commit()
        self.db.refresh(img)
        return img

    def list_products(
        self,
        *,
        q: str | None = None,
        category_id: uuid.UUID | None = None,
        category_slug: str | None = None,
        brand_id: uuid.UUID | None = None,
        brand_slug: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock: bool | None = None,
        skin_type: str | None = None,
        shade: str | None = None,
        featured: bool | None = None,
        new_arrival: bool | None = None,
        best_seller: bool | None = None,
        sort: str = "newest",
        page: int = 1,
        page_size: int = 12,
    ) -> dict:
        query = (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.variants),
            )
            .filter(Product.is_active.is_(True), Product.is_archived.is_(False))
        )

        if category_id:
            query = query.filter(Product.category_id == category_id)
        if category_slug:
            normalized_category_slug = category_slug.strip().lower()
            if normalized_category_slug:
                query = query.join(Product.category).filter(
                    func.lower(Category.slug) == normalized_category_slug,
                    Category.is_active.is_(True),
                )
        if brand_id:
            query = query.filter(Product.brand_id == brand_id)
        if brand_slug:
            normalized_brand_slug = brand_slug.strip().lower()
            if normalized_brand_slug:
                query = query.join(Product.brand).filter(
                    func.lower(Brand.slug) == normalized_brand_slug,
                    Brand.is_active.is_(True),
                )
        if featured is not None:
            query = query.filter(Product.is_featured.is_(featured))
        if new_arrival is not None:
            query = query.filter(Product.is_new_arrival.is_(new_arrival))
        if best_seller is not None:
            query = query.filter(Product.is_best_seller.is_(best_seller))
        if q:
            pattern = f"%{q.strip()}%"
            query = query.filter(
                (Product.name.ilike(pattern)) | (Product.description.ilike(pattern))
            )

        products = query.order_by(Product.created_at.desc()).all()

        # Review stats in single grouped query
        rating_rows = (
            self.db.query(
                Review.product_id,
                func.avg(Review.rating),
                func.count(Review.id),
            )
            .filter(Review.is_approved.is_(True))
            .group_by(Review.product_id)
            .all()
        )
        rating_map = {
            pid: (round(float(avg_r or 0.0), 2), int(cnt or 0))
            for pid, avg_r, cnt in rating_rows
        }

        all_variant_ids = [v.id for p in products for v in p.variants]
        stock_map = _variant_stock_map(self.db, all_variant_ids)

        filtered_summaries: list[ProductSummaryResponse] = []
        for p in products:
            if skin_type and skin_type.lower() not in [s.lower() for s in (p.skin_types or [])]:
                continue
            active_variants = [v for v in p.variants if v.status == "ACTIVE"]
            if shade:
                shade_l = shade.lower()
                if not any(
                    shade_l in (v.shade_name or "").lower()
                    or shade_l in (v.color_name or "").lower()
                    for v in active_variants
                ):
                    continue
            prices = [v.price for v in active_variants]
            min_p = min(prices) if prices else None
            max_p = max(prices) if prices else None
            if min_price is not None and (min_p is None or min_p < min_price):
                continue
            if max_price is not None and (min_p is None or min_p > max_price):
                continue

            has_stock = any(stock_map.get(v.id, 0) > 0 for v in active_variants)
            if in_stock is True and not has_stock:
                continue
            if in_stock is False and has_stock:
                continue

            avg_rating, rev_count = rating_map.get(p.id, (0.0, 0))
            if rev_count == 0 and p.is_demo and isinstance(p.specifications, dict):
                avg_rating = float(p.specifications.get("rating", 0.0) or 0.0)
                rev_count = int(p.specifications.get("review_count", 0) or 0)
            primary_img = next((img.image_url for img in p.images if img.is_primary), None)
            if not primary_img and p.images:
                primary_img = p.images[0].image_url
            orig_prices = [v.original_price for v in active_variants if v.original_price]
            filtered_summaries.append(
                ProductSummaryResponse(
                    id=p.id,
                    name=p.name,
                    slug=p.slug,
                    short_description=p.short_description,
                    category_id=p.category_id,
                    category_name=p.category.name,
                    brand_id=p.brand_id,
                    brand_name=p.brand.name,
                    min_price=min_p,
                    max_price=max_p,
                    original_price=min(orig_prices) if orig_prices else None,
                    primary_image_url=primary_img,
                    average_rating=avg_rating,
                    review_count=rev_count,
                    in_stock=has_stock,
                    is_featured=p.is_featured,
                    is_new_arrival=p.is_new_arrival,
                    is_best_seller=p.is_best_seller,
                    is_demo=p.is_demo,
                    skin_types=p.skin_types or [],
                )
            )

        if sort == "price_asc":
            filtered_summaries.sort(key=lambda item: item.min_price or Decimal("999999"))
        elif sort == "price_desc":
            filtered_summaries.sort(
                key=lambda item: item.min_price or Decimal("0"), reverse=True
            )
        elif sort == "rating":
            filtered_summaries.sort(key=lambda item: item.average_rating, reverse=True)

        total = len(filtered_summaries)
        total_pages = max(1, math.ceil(total / page_size))
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "items": filtered_summaries[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_product_detail(self, product_id: uuid.UUID) -> ProductDetailResponse:
        product = (
            self.db.query(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images),
                joinedload(Product.variants),
            )
            .filter(Product.id == product_id)
            .first()
        )
        if product is None:
            raise NotFoundError("Product not found.")
        stock_map = _variant_stock_map(self.db, [v.id for v in product.variants])
        avg_r, cnt = (
            self.db.query(func.avg(Review.rating), func.count(Review.id))
            .filter(Review.product_id == product.id, Review.is_approved.is_(True))
            .one()
        )
        active_variants = [v for v in product.variants if v.status == "ACTIVE"]
        prices = [v.price for v in active_variants]
        orig_prices = [v.original_price for v in active_variants if v.original_price]
        primary_img = next((img.image_url for img in product.images if img.is_primary), None)
        if not primary_img and product.images:
            primary_img = product.images[0].image_url

        avg_rating = round(float(avg_r or 0.0), 2)
        rev_count = int(cnt or 0)
        if rev_count == 0 and product.is_demo and isinstance(product.specifications, dict):
            avg_rating = float(product.specifications.get("rating", 0.0) or 0.0)
            rev_count = int(product.specifications.get("review_count", 0) or 0)

        return ProductDetailResponse(
            id=product.id,
            name=product.name,
            slug=product.slug,
            short_description=product.short_description,
            description=product.description,
            category_id=product.category_id,
            category_name=product.category.name,
            brand_id=product.brand_id,
            brand_name=product.brand.name,
            min_price=min(prices) if prices else None,
            max_price=max(prices) if prices else None,
            original_price=min(orig_prices) if orig_prices else None,
            primary_image_url=primary_img,
            average_rating=avg_rating,
            review_count=rev_count,
            in_stock=any(stock_map.get(v.id, 0) > 0 for v in active_variants),
            is_featured=product.is_featured,
            is_new_arrival=product.is_new_arrival,
            is_best_seller=product.is_best_seller,
            is_demo=product.is_demo,
            skin_types=product.skin_types or [],
            specifications=product.specifications or {},
            verified_ingredients=product.verified_ingredients,
            images=[
                ProductImageResponse(
                    id=img.id,
                    image_url=img.image_url,
                    alt_text=img.alt_text,
                    is_primary=img.is_primary,
                    sort_order=img.sort_order,
                )
                for img in product.images
            ],
            variants=[
                self._serialize_variant(v, stock_map.get(v.id, 0)) for v in product.variants
            ],
            created_at=product.created_at,
        )

    def list_variants(self, product_id: uuid.UUID) -> list[VariantResponse]:
        variants = (
            self.db.query(ProductVariant)
            .filter(ProductVariant.product_id == product_id)
            .all()
        )
        stock_map = _variant_stock_map(self.db, [v.id for v in variants])
        return [self._serialize_variant(v, stock_map.get(v.id, 0)) for v in variants]

    @staticmethod
    def _serialize_variant(v: ProductVariant, available_qty: int) -> VariantResponse:
        return VariantResponse(
            id=v.id,
            product_id=v.product_id,
            sku=v.sku,
            shade_name=v.shade_name,
            shade_code=v.shade_code,
            color_name=v.color_name,
            hex_color=v.hex_color,
            volume_ml=v.volume_ml,
            weight_g=v.weight_g,
            size=v.size,
            price=v.price,
            original_price=v.original_price,
            is_available=v.is_available and available_qty > 0,
            status=v.status,
            available_quantity=available_qty,
        )

