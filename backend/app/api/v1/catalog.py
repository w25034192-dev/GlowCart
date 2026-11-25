import uuid
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.catalog import (
    BrandCreate,
    BrandResponse,
    BrandUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    PaginatedProductsResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductImageResponse,
    ProductUpdate,
    VariantCreate,
    VariantResponse,
    VariantUpdate,
)
from app.services.catalog_service import CatalogService
from app.services.storage_service import StorageService

router = APIRouter(tags=["Catalog & Products"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return CatalogService(db).list_categories()


@router.post("/admin/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return CatalogService(db).create_category(payload, actor)


@router.put("/admin/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return CatalogService(db).update_category(category_id, payload, actor)


@router.get("/brands", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    return CatalogService(db).list_brands()


@router.post("/admin/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    payload: BrandCreate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return CatalogService(db).create_brand(payload, actor)


@router.put("/admin/brands/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: uuid.UUID,
    payload: BrandUpdate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return CatalogService(db).update_brand(brand_id, payload, actor)


@router.get("/products/search", response_model=PaginatedProductsResponse)
def search_products(
    q: str = Query("", min_length=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return CatalogService(db).list_products(q=q or None, page=page, page_size=page_size)


@router.get("/products", response_model=PaginatedProductsResponse)
def list_products(
    q: str | None = None,
    category_id: uuid.UUID | None = None,
    category_slug: str | None = None,
    brand_id: uuid.UUID | None = None,
    brand_slug: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    in_stock: bool | None = None,
    skin_type: str | None = None,
    shade: str | None = None,
    featured: bool | None = None,
    new_arrival: bool | None = None,
    best_seller: bool | None = None,
    sort: str = Query("newest", pattern="^(newest|price_asc|price_desc|rating)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from decimal import Decimal

    return CatalogService(db).list_products(
        q=q,
        category_id=category_id,
        category_slug=category_slug,
        brand_id=brand_id,
        brand_slug=brand_slug,
        min_price=Decimal(str(min_price)) if min_price is not None else None,
        max_price=Decimal(str(max_price)) if max_price is not None else None,
        in_stock=in_stock,
        skin_type=skin_type,
        shade=shade,
        featured=featured,
        new_arrival=new_arrival,
        best_seller=best_seller,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    return CatalogService(db).get_product_detail(product_id)


@router.post("/admin/products", status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    product = CatalogService(db).create_product(payload, actor)
    return {"id": str(product.id), "name": product.name, "slug": product.slug}


@router.put("/admin/products/{product_id}")
def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    product = CatalogService(db).update_product(product_id, payload, actor)
    return {"id": str(product.id), "name": product.name, "slug": product.slug}


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    CatalogService(db).archive_product(product_id, actor)


@router.post(
    "/admin/products/{product_id}/images",
    response_model=ProductImageResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_product_image(
    product_id: uuid.UUID,
    file: UploadFile = File(...),
    alt_text: str | None = Form(default=None),
    is_primary: bool = Form(default=False),
    _actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    image_url = StorageService().save_product_image(file)
    return CatalogService(db).add_product_image(
        product_id=product_id,
        image_url=image_url,
        alt_text=alt_text,
        is_primary=is_primary,
    )


@router.get("/products/{product_id}/variants", response_model=list[VariantResponse])
def list_product_variants(product_id: uuid.UUID, db: Session = Depends(get_db)):
    return CatalogService(db).list_variants(product_id)


@router.post("/admin/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    payload: VariantCreate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return CatalogService(db).create_variant(payload, actor)


@router.put("/admin/variants/{variant_id}", response_model=VariantResponse)
def update_variant(
    variant_id: uuid.UUID,
    payload: VariantUpdate,
    actor: User = Depends(require_roles("admin", "super_admin")),
    db: Session = Depends(get_db),
):
    return CatalogService(db).update_variant(variant_id, payload, actor)

