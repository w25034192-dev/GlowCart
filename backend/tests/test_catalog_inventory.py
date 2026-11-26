from datetime import date, timedelta
import io


def _login_as(client, make_user, email: str, role_name: str) -> dict[str, str]:
    make_user(email, role_name=role_name)
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "GlowCartPass123!"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_catalog_crud_and_filtering(client, make_user):
    cust_headers = _login_as(client, make_user, "cust_cat@glowcart.com", "customer")
    admin_headers = _login_as(client, make_user, "admin_cat@glowcart.com", "admin")

    # Customer cannot create category
    forbidden = client.post(
        "/api/v1/admin/categories",
        json={"name": "Makeup", "slug": "makeup"},
        headers=cust_headers,
    )
    assert forbidden.status_code == 403

    cat_res = client.post(
        "/api/v1/admin/categories",
        json={"name": "Makeup", "slug": "makeup", "description": "Face and lip cosmetics"},
        headers=admin_headers,
    )
    assert cat_res.status_code == 201
    category_id = cat_res.json()["id"]

    brand_res = client.post(
        "/api/v1/admin/brands",
        json={"name": "Rare Beauty", "slug": "rare-beauty", "country_of_origin": "USA", "is_featured": True},
        headers=admin_headers,
    )
    assert brand_res.status_code == 201
    brand_id = brand_res.json()["id"]

    prod_res = client.post(
        "/api/v1/admin/products",
        json={
            "category_id": category_id,
            "brand_id": brand_id,
            "name": "Soft Pinch Liquid Blush",
            "slug": "soft-pinch-liquid-blush",
            "description": "Weightless liquid blush with buildable pigment.",
            "skin_types": ["all", "dry", "combination"],
            "is_featured": True,
        },
        headers=admin_headers,
    )
    assert prod_res.status_code == 201
    product_id = prod_res.json()["id"]

    var1 = client.post(
        "/api/v1/admin/variants",
        json={
            "product_id": product_id,
            "sku": "RB-BLUSH-JOY",
            "shade_name": "Joy",
            "shade_code": "RB01",
            "color_name": "Muted Peach",
            "hex_color": "#E47A68",
            "volume_ml": 7,
            "price": "23.00",
            "original_price": "26.00",
        },
        headers=admin_headers,
    )
    assert var1.status_code == 201

    var2 = client.post(
        "/api/v1/admin/variants",
        json={
            "product_id": product_id,
            "sku": "RB-BLUSH-HOPE",
            "shade_name": "Hope",
            "shade_code": "RB02",
            "color_name": "Nude Mauve",
            "hex_color": "#C97A7E",
            "volume_ml": 7,
            "price": "25.00",
        },
        headers=admin_headers,
    )
    assert var2.status_code == 201

    # Search and filter
    search = client.get("/api/v1/products/search?q=Blush")
    assert search.status_code == 200
    assert search.json()["total"] == 1

    by_skin = client.get("/api/v1/products?skin_type=dry&min_price=20&max_price=24")
    assert by_skin.status_code == 200
    assert len(by_skin.json()["items"]) == 1

    variants = client.get(f"/api/v1/products/{product_id}/variants")
    assert variants.status_code == 200
    assert len(variants.json()) == 2


def test_inventory_batches_expiry_and_fefo_allocation(client, make_user, db_session):
    from app.services.inventory_service import InventoryService

    admin_headers = _login_as(client, make_user, "admin_inv@glowcart.com", "admin")
    cat_id = client.post(
        "/api/v1/admin/categories",
        json={"name": "Skincare", "slug": "skincare"},
        headers=admin_headers,
    ).json()["id"]
    brand_id = client.post(
        "/api/v1/admin/brands",
        json={"name": "COSRX", "slug": "cosrx"},
        headers=admin_headers,
    ).json()["id"]
    prod_id = client.post(
        "/api/v1/admin/products",
        json={
            "category_id": cat_id,
            "brand_id": brand_id,
            "name": "Advanced Snail 96 Mucin Essence",
            "slug": "cosrx-snail-mucin",
            "description": "Hydrating essence.",
            "skin_types": ["dry", "sensitive"],
        },
        headers=admin_headers,
    ).json()["id"]
    variant_id = client.post(
        "/api/v1/admin/variants",
        json={
            "product_id": prod_id,
            "sku": "COSRX-SNAIL-100",
            "volume_ml": 100,
            "price": "25.00",
        },
        headers=admin_headers,
    ).json()["id"]

    # Receive expired batch -> cannot be sold
    expired_date = (date.today() - timedelta(days=5)).isoformat()
    soon_date = (date.today() + timedelta(days=20)).isoformat()
    later_date = (date.today() + timedelta(days=200)).isoformat()
    mfg_date = (date.today() - timedelta(days=90)).isoformat()

    r_exp = client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-EXPIRED",
            "manufacture_date": mfg_date,
            "expiry_date": expired_date,
            "quantity": 5,
        },
        headers=admin_headers,
    )
    assert r_exp.status_code == 201

    # Negative adjustment should fail
    neg = client.post(
        "/api/v1/admin/inventory/adjustments",
        json={
            "variant_id": variant_id,
            "quantity_delta": -99,
            "reason": "Invalid deduction test",
        },
        headers=admin_headers,
    )
    assert neg.status_code == 409

    # Receive two sellable batches (FEFO: soon_date before later_date)
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-LATER",
            "manufacture_date": mfg_date,
            "expiry_date": later_date,
            "quantity": 4,
        },
        headers=admin_headers,
    )
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-SOON",
            "manufacture_date": mfg_date,
            "expiry_date": soon_date,
            "quantity": 3,
        },
        headers=admin_headers,
    )

    expiring = client.get("/api/v1/admin/inventory/expiring", headers=admin_headers)
    assert expiring.status_code == 200
    assert len(expiring.json()["expired"]) == 1
    assert len(expiring.json()["expiring_soon"]) == 1

    # Sellable stock excludes expired batch (3 + 4 = 7)
    inv_service = InventoryService(db_session)
    assert inv_service.get_sellable_quantity(variant_id) == 7

    # Allocate 5 units via FEFO -> consumes all 3 from BATCH-SOON and 2 from BATCH-LATER
    allocations = inv_service.allocate_and_deduct_fefo(
        variant_id=variant_id,
        quantity=5,
        actor_id=None,
        reference_type="test",
        reference_id="fefo-1",
    )
    db_session.commit()
    assert allocations[0][0].batch_number == "BATCH-SOON"
    assert allocations[0][1] == 3
    assert allocations[1][0].batch_number == "BATCH-LATER"
    assert allocations[1][1] == 2
    assert inv_service.get_sellable_quantity(variant_id) == 2


def test_product_image_upload_validation(client, make_user):
    admin_headers = _login_as(client, make_user, "admin_img@glowcart.com", "admin")
    cat_id = client.post(
        "/api/v1/admin/categories",
        json={"name": "Sun Care", "slug": "sun-care"},
        headers=admin_headers,
    ).json()["id"]
    brand_id = client.post(
        "/api/v1/admin/brands",
        json={"name": "Beauty of Joseon", "slug": "boj"},
        headers=admin_headers,
    ).json()["id"]
    prod_id = client.post(
        "/api/v1/admin/products",
        json={
            "category_id": cat_id,
            "brand_id": brand_id,
            "name": "Relief Sun",
            "slug": "relief-sun",
            "description": "Lightweight SPF.",
        },
        headers=admin_headers,
    ).json()["id"]

    bad_upload = client.post(
        f"/api/v1/admin/products/{prod_id}/images",
        files={"file": ("payload.exe", io.BytesIO(b"MZ123"), "application/octet-stream")},
        headers=admin_headers,
    )
    assert bad_upload.status_code == 400


def test_demo_seeder_meets_minimum_catalog_counts(db_session):
    from app.db.seed import seed_demo_data
    from app.models import Brand, Category, Product, ProductVariant

    seed_demo_data(db_session)
    assert db_session.query(Category).count() >= 8
    assert db_session.query(Brand).count() >= 15
    assert db_session.query(Product).count() >= 50
    assert db_session.query(ProductVariant).count() >= 100


def test_ensure_initial_data_seeds_when_empty_and_creates_default_admin(db_session):
    from app.db.seed import ensure_initial_data
    from app.models import Category, Product, ProductImage, Role, User

    assert db_session.query(Product).count() == 0
    ensure_initial_data(db_session)

    admin_role = db_session.query(Role).filter(Role.name == "admin").one()
    assert db_session.query(User).filter(User.role_id == admin_role.id).count() >= 1
    assert db_session.query(Product).count() >= 50

    cat_names = {c.name for c in db_session.query(Category).all()}
    for required in ("Makeup", "Skincare", "Sun Care", "Hair Care", "Fragrance"):
        assert required in cat_names

    images = db_session.query(ProductImage).all()
    assert len(images) >= 50
    assert all(img.image_url and (img.image_url.startswith("https://") or img.image_url.startswith("/images/")) for img in images)

    # Calling a second time is idempotent
    before_count = db_session.query(Product).count()
    ensure_initial_data(db_session)
    assert db_session.query(Product).count() == before_count


def test_all_seeded_categories_and_skincare_endpoint_consistency(client, db_session):
    from app.db.seed import CATEGORIES_DATA, CATALOG_BLUEPRINT, seed_demo_data

    seed_demo_data(db_session)
    expected_skincare = len([e for e in CATALOG_BLUEPRINT if e[0] == "Skincare"])

    cat_res = client.get("/api/v1/categories")
    assert cat_res.status_code == 200
    categories = cat_res.json()
    slugs = {c["slug"]: c for c in categories}
    for _name, slug, _desc, _order in CATEGORIES_DATA:
        assert slug in slugs
        assert slugs[slug]["is_active"] is True

    assert "skincare" in slugs
    assert slugs["skincare"]["name"] == "Skincare"

    seen_product_ids: set[str] = set()
    for cat in categories:
        prod_res = client.get(
            "/api/v1/products",
            params={"category_slug": cat["slug"], "page": 1, "page_size": 50},
        )
        assert prod_res.status_code == 200
        body = prod_res.json()
        assert body["total"] > 0, f"Expected > 0 products for category {cat['slug']}"
        assert len(body["items"]) == min(body["total"], 50)
        for item in body["items"]:
            assert item["category_id"] == cat["id"]
            assert item["category_name"] == cat["name"]
            assert item["in_stock"] is True
            assert item["primary_image_url"]
            assert item["id"] not in seen_product_ids
            seen_product_ids.add(item["id"])

    skincare_res = client.get("/api/v1/products", params={"category_slug": "skincare"})
    assert skincare_res.status_code == 200
    assert skincare_res.json()["total"] == expected_skincare

    # Case-insensitive and whitespace-trimmed slug lookup
    mixed_res = client.get("/api/v1/products", params={"category_slug": " Skincare "})
    assert mixed_res.status_code == 200
    assert mixed_res.json()["total"] == expected_skincare


def test_ensure_initial_data_recovers_missing_skincare_when_other_products_exist(db_session):
    from app.db.seed import CATALOG_BLUEPRINT, ensure_initial_data
    from app.models import Brand, Category, Product

    makeup = Category(name="Makeup", slug="makeup", sort_order=1, is_active=True)
    brand = Brand(name="Custom Brand", slug="custom-brand", is_active=True)
    db_session.add_all([makeup, brand])
    db_session.flush()
    existing_prod = Product(
        category_id=makeup.id,
        brand_id=brand.id,
        name="Custom Lip Oil",
        slug="custom-lip-oil",
        description="Pre-existing non-skincare product.",
        skin_types=["all"],
        specifications={},
        is_active=True,
        is_archived=False,
        is_demo=False,
    )
    db_session.add(existing_prod)
    db_session.commit()

    seeded = ensure_initial_data(db_session)
    assert seeded is True
    skincare_cat = db_session.query(Category).filter(Category.slug == "skincare").first()
    assert skincare_cat is not None
    skincare_products = (
        db_session.query(Product).filter(Product.category_id == skincare_cat.id).all()
    )
    expected_skincare = len([e for e in CATALOG_BLUEPRINT if e[0] == "Skincare"])
    assert len(skincare_products) == expected_skincare
    # Existing product preserved with zero duplicates
    assert db_session.query(Product).filter(Product.slug == "custom-lip-oil").count() == 1


def test_all_50_seeded_products_accessible_via_pagination(client, db_session):
    from app.db.seed import CATALOG_BLUEPRINT, seed_demo_data

    seed_demo_data(db_session)
    total_expected = len(CATALOG_BLUEPRINT)
    page_size = 12
    total_pages = (total_expected + page_size - 1) // page_size

    collected_ids: set[str] = set()
    for page in range(1, total_pages + 1):
        res = client.get("/api/v1/products", params={"page": page, "page_size": page_size})
        assert res.status_code == 200
        payload = res.json()
        assert payload["total"] == total_expected
        assert payload["page"] == page
        assert payload["page_size"] == page_size
        assert payload["total_pages"] == total_pages
        expected_len = page_size if page < total_pages else (total_expected - (page - 1) * page_size)
        assert len(payload["items"]) == expected_len
        for item in payload["items"]:
            collected_ids.add(item["id"])

    assert len(collected_ids) == total_expected


def test_generate_100_products_and_seeder(db_session):
    from app.db.seed import (
        BRANDS,
        CATEGORIES,
        CATEGORY_CATALOG,
        generate_100_products,
        generate_single_product,
        seed_generated_products,
    )
    from app.models import Product, ProductVariant, InventoryBatch

    # Test single product generator
    single = generate_single_product()
    assert single["category"] in CATEGORY_CATALOG
    assert single["brand"] in BRANDS
    assert single["image_url"] in CATEGORY_CATALOG[single["category"]]["images"]

    # Test single product with explicit category
    single_makeup = generate_single_product(index=42, category="Makeup")
    assert single_makeup["category"] == "Makeup"
    assert single_makeup["name"].endswith("#42")
    assert single_makeup["image_url"] in CATEGORY_CATALOG["Makeup"]["images"]

    products = generate_100_products()
    assert len(products) == 100
    assert all(p["brand"] in BRANDS for p in products)
    assert all(p["category"] in CATEGORIES for p in products)
    assert all(18.0 <= p["price"] <= 68.0 for p in products)
    assert all(20 <= p["stock"] <= 120 for p in products)
    assert sum(1 for p in products if p["is_popular"]) == 20
    assert all("image_url" in p for p in products)

    # Seed subset into db to verify model persistence
    created = seed_generated_products(db_session, products[:10])
    assert created == 10
    assert db_session.query(Product).count() >= 10
    assert db_session.query(ProductVariant).count() >= 10
    assert db_session.query(InventoryBatch).count() >= 10


def test_products_data_json_and_loader(db_session):
    from app.db.seed import load_products_from_json, seed_generated_products
    from app.models import Product, ProductVariant, ProductImage
    products = load_products_from_json()
    assert isinstance(products, list)
    assert len(products) >= 6

    by_name = {p["name"]: p for p in products}

    # Verify iconic products exist in products_data.json
    dior_oil = by_name.get("Dior Addict Lip Glow Oil")
    assert dior_oil is not None
    assert dior_oil["brand"] == "DIOR"
    assert dior_oil["category"] == "Makeup"
    assert dior_oil["price"] == 40.0
    assert dior_oil["shade_name"] == "001 Pink"
    assert dior_oil["shade_hex"] == "#F4A6B8"

    rare = by_name.get("Rare Beauty Soft Pinch Liquid Blush")
    assert rare is not None
    assert rare["brand"] == "RARE BEAUTY"
    assert rare["price"] == 23.0
    assert rare["shade_name"] == "Joy"

    assert any("Charlotte Tilbury" in p["brand"] or "CHARLOTTE TILBURY" in p["brand"] for p in products)
    assert any("Estée Lauder" in p["brand"] or "ESTÉE LAUDER" in p["brand"] for p in products)
    assert any("Chanel" in p["brand"] or "CHANEL" in p["brand"] for p in products)
    assert any("Laneige" in p["brand"] or "LANEIGE" in p["brand"] for p in products)

    # Seed subset into db to verify persistence
    created = seed_generated_products(db_session, products[:6])
    assert created >= 1
    assert db_session.query(Product).count() >= 1


def test_ensure_initial_data_and_generated_seed_survive_sku_collisions(db_session):
    """Simulate an existing Railway DB where old products already own GC-001-01 and GC-GEN-001."""
    from decimal import Decimal
    from app.db.seed import (
        CATALOG_BLUEPRINT,
        _ensure_categories_and_brands,
        ensure_initial_data,
        generate_single_product,
        seed_generated_products,
    )
    from app.models import Product, ProductVariant

    cat_map, brand_map = _ensure_categories_and_brands(db_session)
    legacy_prod = Product(
        category_id=cat_map["Skincare"].id,
        brand_id=next(iter(brand_map.values())).id,
        name="Legacy Pre-Existing Product",
        slug="legacy-pre-existing-product",
        short_description="Legacy item",
        description="Already in DB before new blueprint items",
        skin_types=["all"],
        specifications={},
        is_demo=False,
    )
    db_session.add(legacy_prod)
    db_session.flush()

    db_session.add(
        ProductVariant(
            product_id=legacy_prod.id,
            sku="GC-001-01",
            price=Decimal("10.00"),
            is_available=True,
            status="ACTIVE",
        )
    )
    db_session.add(
        ProductVariant(
            product_id=legacy_prod.id,
            sku="GC-GEN-001",
            price=Decimal("12.00"),
            is_available=True,
            status="ACTIVE",
        )
    )
    db_session.commit()

    seeded = ensure_initial_data(db_session)
    assert seeded is True
    assert db_session.query(Product).count() == len(CATALOG_BLUEPRINT) + 1

    extra = [generate_single_product(index=1, category="Skincare")]
    created_gen = seed_generated_products(db_session, extra)
    assert created_gen == 1
    assert db_session.query(Product).count() == len(CATALOG_BLUEPRINT) + 2


def test_ensure_minimum_product_count_tops_up_from_70_to_100(db_session):
    """When DB has 70 existing products, ensure_minimum_product_count adds only 30 to reach 100."""
    from app.db.seed import (
        ensure_minimum_product_count,
        generate_single_product,
        seed_generated_products,
    )
    from app.models import Product

    initial_70 = [generate_single_product(index=i) for i in range(1, 71)]
    seed_generated_products(db_session, initial_70)
    before_count = db_session.query(Product).count()
    assert before_count == 70

    added = ensure_minimum_product_count(db_session, target_count=100)
    assert added == 30
    assert db_session.query(Product).count() == 100

    # Calling again when already at 100 should add 0
    added_again = ensure_minimum_product_count(db_session, target_count=100)
    assert added_again == 0
    assert db_session.query(Product).count() == 100


def test_repair_duplicate_product_images_replaces_repeated_fallback_urls(db_session):
    """Startup repair check replaces repeated/broken fallback URLs with diverse category pool URLs."""
    from app.db.seed import (
        CATEGORY_IMAGE_POOLS,
        _ensure_categories_and_brands,
        repair_duplicate_product_images,
        resolve_seed_image_url,
    )
    from app.models import Product, ProductImage

    # Each primary category pool must have at least 15 unique verified URLs
    for cat_name in ("Makeup", "Skincare", "Sun Care", "Hair Care", "Fragrance", "Body Care", "Beauty Tools"):
        assert len(set(CATEGORY_IMAGE_POOLS[cat_name])) >= 15

    # Adjacent products in the same category should resolve to distinct image URLs
    sample_names = [
        ("Skincare Hydrating Serum", "skincare-hydrating-serum"),
        ("Skincare Calming Toner", "skincare-calming-toner"),
        ("Skincare Barrier Cream", "skincare-barrier-cream"),
        ("Skincare Gentle Cleanser", "skincare-gentle-cleanser"),
        ("Skincare Lip Sleeping Mask", "skincare-lip-sleeping-mask"),
    ]
    resolved_urls = [
        resolve_seed_image_url("Skincare", pname, pslug, index=i)
        for i, (pname, pslug) in enumerate(sample_names, start=1)
    ]
    assert len(set(resolved_urls)) >= 4

    cat_map, brand_map = _ensure_categories_and_brands(db_session)
    brand = next(iter(brand_map.values()))
    repeated_url = "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80"

    for i, (pname, pslug) in enumerate(sample_names, start=1):
        prod = Product(
            category_id=cat_map["Skincare"].id,
            brand_id=brand.id,
            name=pname,
            slug=pslug,
            description="Test product",
            skin_types=["all"],
            specifications={},
            is_demo=True,
        )
        db_session.add(prod)
        db_session.flush()
        db_session.add(ProductImage(product_id=prod.id, image_url=repeated_url, is_primary=True, sort_order=0))
    db_session.commit()

    repaired = repair_duplicate_product_images(db_session)
    assert repaired >= 4

    final_urls = [img.image_url for img in db_session.query(ProductImage).all()]
    assert len(set(final_urls)) >= 4


def test_fenty_showcase_and_portrait_only_urls_replaced(db_session):
    """Ensure portrait-only URLs are excluded and replaced with product-in-hand showcase images."""
    from app.db.seed import (
        CATEGORY_IMAGE_POOLS,
        VERIFIED_COSMETIC_IMAGE_URLS,
        _ensure_categories_and_brands,
        repair_duplicate_product_images,
        resolve_seed_image_url,
    )
    from app.models import Product, ProductImage

    portrait_only_urls = {
        "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=800&q=80",
    }
    assert portrait_only_urls.isdisjoint(set(VERIFIED_COSMETIC_IMAGE_URLS))
    for pool in CATEGORY_IMAGE_POOLS.values():
        assert portrait_only_urls.isdisjoint(set(pool))

    assert (
        resolve_seed_image_url("Makeup", "Fenty Beauty Pro Filt'r", "fenty-pro-filtr-soft-matte-foundation")
        == "/images/products/fenty-foundation-hand.jpg"
    )

    cat_map, brand_map = _ensure_categories_and_brands(db_session)
    brand = next(iter(brand_map.values()))
    fenty = Product(
        category_id=cat_map["Makeup"].id,
        brand_id=brand.id,
        name="Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation",
        slug="fenty-pro-filtr-soft-matte-foundation",
        description="Foundation",
        skin_types=["oily"],
        specifications={},
        is_demo=True,
    )
    db_session.add(fenty)
    db_session.flush()
    old_portrait = next(iter(portrait_only_urls))
    db_session.add(ProductImage(product_id=fenty.id, image_url=old_portrait, is_primary=True, sort_order=0))
    db_session.commit()

    repaired = repair_duplicate_product_images(db_session)
    assert repaired == 1
    updated = db_session.query(ProductImage).filter(ProductImage.product_id == fenty.id).one()
    assert updated.image_url == "/images/products/fenty-foundation-hand.jpg"


def test_cleanup_generic_products_and_curated_100_blueprint(db_session):
    """Startup cleanup removes generic #N products while keeping orders safe, and blueprint has >=100 unique items."""
    from app.db.seed import (
        CATALOG_BLUEPRINT,
        cleanup_generic_generated_products,
        ensure_initial_data,
        generate_single_product,
        seed_generated_products,
    )
    from app.models import Product

    # 1. Blueprint itself must have >= 100 unique real products with zero duplicate names/slugs
    assert len(CATALOG_BLUEPRINT) >= 100
    names = [e[2] for e in CATALOG_BLUEPRINT]
    slugs = [e[3] for e in CATALOG_BLUEPRINT]
    assert len(set(names)) == len(CATALOG_BLUEPRINT)
    assert len(set(slugs)) == len(CATALOG_BLUEPRINT)
    lower_names = {n.lower() for n in names}
    for required in (
        "charlotte tilbury airbrush flawless setting spray",
        "mac matte lipstick velvet teddy",
        "estée lauder advanced night repair serum",
        "medicube collagen jelly cream",
    ):
        assert required in lower_names

    # 2. Simulate old generic #N generated products in live DB
    generic_items = [generate_single_product(index=i) for i in range(1, 11)]
    seed_generated_products(db_session, generic_items)
    assert db_session.query(Product).filter(Product.name.like("%#1%")).count() >= 1

    cleaned = cleanup_generic_generated_products(db_session)
    assert cleaned == 10
    assert db_session.query(Product).filter(Product.name.like("%#1%")).count() == 0

    ensure_initial_data(db_session)
    assert db_session.query(Product).filter(Product.is_active.is_(True), Product.is_archived.is_(False)).count() >= 100


def test_strict_item_type_image_matching_and_no_competing_logos(db_session):
    """Ensure products strictly match their item-type photo and never show competing brand logos."""
    from app.db.seed import (
        _ensure_categories_and_brands,
        repair_duplicate_product_images,
        resolve_seed_image_url,
    )
    from app.models import Product, ProductImage

    clinique_url = "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80"
    hair_woman_url = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80"
    eyeliner_url = "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=800&q=80"

    assert (
        resolve_seed_image_url("Makeup", "Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation", "fenty-pro-filtr-soft-matte-foundation")
        == "/images/products/fenty-foundation-hand.jpg"
    )
    mac_url = resolve_seed_image_url("Makeup", "MAC Matte Lipstick Velvet Teddy", "mac-matte-lipstick-velvet-teddy")
    assert mac_url == "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=800&q=80"
    ct_url = resolve_seed_image_url("Makeup", "Charlotte Tilbury Airbrush Flawless Setting Spray", "ct-airbrush-flawless-setting-spray")
    assert ct_url != clinique_url

    cat_map, brand_map = _ensure_categories_and_brands(db_session)
    brand = next(iter(brand_map.values()))
    mismatches = [
        ("Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation", "fenty-pro-filtr-soft-matte-foundation", hair_woman_url),
        ("MAC Matte Lipstick Velvet Teddy", "mac-matte-lipstick-velvet-teddy", hair_woman_url),
        ("Charlotte Tilbury Airbrush Flawless Setting Spray", "ct-airbrush-flawless-setting-spray", clinique_url),
    ]
    for pname, pslug, bad_url in mismatches:
        p = Product(
            category_id=cat_map["Makeup"].id,
            brand_id=brand.id,
            name=pname,
            slug=pslug,
            description="Test",
            skin_types=["all"],
            specifications={},
            is_demo=True,
        )
        db_session.add(p)
        db_session.flush()
        db_session.add(ProductImage(product_id=p.id, image_url=bad_url, is_primary=True, sort_order=0))
    db_session.commit()

    repaired = repair_duplicate_product_images(db_session)
    assert repaired == 3

    for _pname, pslug, bad_url in mismatches:
        prod = db_session.query(Product).filter(Product.slug == pslug).one()
        img = db_session.query(ProductImage).filter(ProductImage.product_id == prod.id).one()
        assert img.image_url != bad_url


def test_zero_duplicate_image_urls_across_full_catalog_and_lip_matching(db_session):
    """Ensure every product in the catalog has a unique image_url and lip/foundation items match cleanly."""
    from app.db.seed import ensure_initial_data, resolve_seed_image_url
    from app.models import Product, ProductImage

    # Lip items like Matte Ink and Gloss Bomb must never resolve to eyeliner or brush flatlay
    eyeliner_url = "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=800&q=80"
    brush_flatlay_url = "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80"

    gloss_url = resolve_seed_image_url("Makeup", "Fenty Beauty Gloss Bomb Universal Lip Luminizer", "fenty-gloss-bomb-luminizer")
    matte_ink_url = resolve_seed_image_url("Makeup", "Rhode Peptide Lip Tint Espresso", "rhode-peptide-lip-tint")
    assert gloss_url not in (eyeliner_url, brush_flatlay_url)
    assert matte_ink_url not in (eyeliner_url, brush_flatlay_url)

    ensure_initial_data(db_session)
    all_images = db_session.query(ProductImage).all()
    all_urls = [img.image_url for img in all_images]
    assert len(all_urls) == 100
    assert len(set(all_urls)) == 100

    # Verify Beauty Tools has 10 distinct items with 10 unique images
    beauty_tools = [p for p in db_session.query(Product).all() if p.category.slug == "beauty-tools"]
    assert len(beauty_tools) == 10
    tool_urls = [db_session.query(ProductImage).filter(ProductImage.product_id == p.id).one().image_url for p in beauty_tools]
    assert len(set(tool_urls)) == 10


def test_all_seeded_products_have_unique_image_urls_and_type_groups(db_session):
    """Verify all 12 product-type image groups exist and every seeded product gets a distinct image_url."""
    from app.db.seed import PRODUCT_TYPE_IMAGE_POOLS, seed_demo_data
    from app.models import Product, ProductImage

    expected_groups = {
        "serum_ampoule",
        "toner_essence",
        "moisturizer_cream",
        "cleanser",
        "sunscreen",
        "foundation_concealer",
        "blush_powder",
        "lipstick_gloss",
        "eye_makeup",
        "hair_care",
        "perfume",
        "body_tools",
    }
    assert expected_groups.issubset(set(PRODUCT_TYPE_IMAGE_POOLS.keys()))

    seed_demo_data(db_session)
    products = db_session.query(Product).all()
    images = db_session.query(ProductImage).filter(ProductImage.is_primary.is_(True)).all()
    unique_urls = {img.image_url for img in images}
    assert len(products) == 100
    assert len(unique_urls) == len(products)


def test_products_100_hardcoded_unique_urls_and_startup_force_refresh(db_session):
    """Verify PRODUCTS_100 has 100 unique products & Unsplash URLs, and sync_catalog_100 force-refreshes stale DB rows."""
    from app.db.seed import PRODUCTS_100, _ensure_categories_and_brands, ensure_initial_data
    from app.models import Product, ProductImage

    assert len(PRODUCTS_100) == 100
    assert len({p["image_url"] for p in PRODUCTS_100}) == 100
    assert len({p["name"] for p in PRODUCTS_100}) == 100
    assert len({p["slug"] for p in PRODUCTS_100}) == 100
    for p in PRODUCTS_100:
        assert p["image_url"].startswith(("https://", "/images/products/"))

    # Seed initial 100 products, then corrupt one image and insert a stale duplicate product
    ensure_initial_data(db_session)
    cat_map, brand_map = _ensure_categories_and_brands(db_session)
    brand = next(iter(brand_map.values()))

    brush = db_session.query(Product).filter(Product.slug == "hourglass-vanish-foundation-brush").one()
    brush_img = db_session.query(ProductImage).filter(ProductImage.product_id == brush.id).one()
    brush_img.image_url = "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80"

    stale = Product(
        category_id=cat_map["Beauty Tools"].id,
        brand_id=brand.id,
        name="NYX Marshmellow Blending Sponge",
        slug="nyx-blending-sponge",
        description="Old duplicate sponge",
        skin_types=["all"],
        specifications={},
        is_demo=True,
    )
    db_session.add(stale)
    db_session.commit()

    # Startup sync must delete the stale duplicate and force-refresh Hourglass brush back to its 1-to-1 URL
    changed = ensure_initial_data(db_session)
    assert changed is True
    assert db_session.query(Product).filter(Product.slug == "nyx-blending-sponge").first() is None
    refreshed_img = db_session.query(ProductImage).filter(ProductImage.product_id == brush.id).one()
    expected_brush_url = next(p["image_url"] for p in PRODUCTS_100 if p["slug"] == "hourglass-vanish-foundation-brush")
    assert refreshed_img.image_url == expected_brush_url

    # Verify realistic seeded ratings (4.7-4.9) and review counts (95-450) via CatalogService
    from app.services.catalog_service import CatalogService
    listed = CatalogService(db_session).list_products(page=1, page_size=20)
    assert len(listed["items"]) == 20
    for item in listed["items"]:
        assert 4.7 <= item.average_rating <= 4.9
        assert 95 <= item.review_count <= 450











