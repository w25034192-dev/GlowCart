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



