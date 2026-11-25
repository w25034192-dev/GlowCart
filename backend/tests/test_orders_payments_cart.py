from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import json

from app.core.config import get_settings
from app.core.security import sign_webhook_payload


def _setup_catalog_and_users(client, make_user):
    cust = make_user("buyer@glowcart.com", role_name="customer")
    admin = make_user("ops@glowcart.com", role_name="admin")

    cust_tok = client.post(
        "/api/v1/auth/login",
        json={"email": "buyer@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    admin_tok = client.post(
        "/api/v1/auth/login",
        json={"email": "ops@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    ch = {"Authorization": f"Bearer {cust_tok}"}
    ah = {"Authorization": f"Bearer {admin_tok}"}

    cat_id = client.post(
        "/api/v1/admin/categories",
        json={"name": "Makeup", "slug": "makeup-test"},
        headers=ah,
    ).json()["id"]
    brand_id = client.post(
        "/api/v1/admin/brands",
        json={"name": "Fenty Test", "slug": "fenty-test"},
        headers=ah,
    ).json()["id"]
    prod_id = client.post(
        "/api/v1/admin/products",
        json={
            "category_id": cat_id,
            "brand_id": brand_id,
            "name": "Gloss Bomb Universal Lip Luminizer",
            "slug": "gloss-bomb-test",
            "description": "High-shine lip gloss.",
        },
        headers=ah,
    ).json()["id"]
    variant_id = client.post(
        "/api/v1/admin/variants",
        json={
            "product_id": prod_id,
            "sku": "FB-GLOSS-01",
            "shade_name": "Fenty Glow",
            "hex_color": "#C97F73",
            "price": "25.00",
        },
        headers=ah,
    ).json()["id"]

    addr_id = client.post(
        "/api/v1/addresses",
        json={
            "label": "Home",
            "recipient_name": "Buyer One",
            "phone": "+1-555-0200",
            "line1": "500 Glow St",
            "city": "Los Angeles",
            "state": "CA",
            "postal_code": "90001",
            "country": "USA",
            "is_default": True,
        },
        headers=ch,
    ).json()["id"]

    return cust, admin, ch, ah, prod_id, variant_id, addr_id


def test_cart_wishlist_coupon_and_cod_order_snapshot(client, make_user):
    _c, _a, ch, ah, prod_id, variant_id, addr_id = _setup_catalog_and_users(client, make_user)

    # Receive stock batch (5 units)
    today = date.today()
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-FB-01",
            "manufacture_date": (today - timedelta(days=30)).isoformat(),
            "expiry_date": (today + timedelta(days=300)).isoformat(),
            "quantity": 5,
        },
        headers=ah,
    )

    # Wishlist
    w_add = client.post(
        "/api/v1/wishlist/items",
        json={"product_id": prod_id},
        headers=ch,
    )
    assert w_add.status_code == 201
    assert len(client.get("/api/v1/wishlist", headers=ch).json()["items"]) == 1

    # Coupon
    now = datetime.now(timezone.utc)
    client.post(
        "/api/v1/admin/promotions",
        json={
            "title": "Lip Promo",
            "discount_type": "PERCENTAGE",
            "discount_value": "10.00",
            "starts_at": (now - timedelta(days=1)).isoformat(),
            "ends_at": (now + timedelta(days=10)).isoformat(),
            "coupon_code": "LIP10",
            "min_order_amount": "20.00",
        },
        headers=ah,
    )

    # Cart
    add = client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 2},
        headers=ch,
    )
    assert add.status_code == 201
    cart = client.get("/api/v1/cart?coupon_code=LIP10", headers=ch).json()
    assert float(cart["subtotal"]) == 50.00
    assert float(cart["discount_amount"]) == 5.00

    # Place COD order with idempotency key
    order_res = client.post(
        "/api/v1/orders",
        json={
            "address_id": addr_id,
            "payment_method": "COD",
            "coupon_code": "LIP10",
            "idempotency_key": "idem-cod-001",
        },
        headers=ch,
    )
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["id"]
    assert order_data["status"] == "CONFIRMED"
    assert order_data["payment_status"] == "UNPAID"
    assert float(order_data["items"][0]["unit_price"]) == 25.00

    # Idempotent replay returns same order
    replay = client.post(
        "/api/v1/orders",
        json={
            "address_id": addr_id,
            "payment_method": "COD",
            "coupon_code": "LIP10",
            "idempotency_key": "idem-cod-001",
        },
        headers=ch,
    )
    assert replay.status_code == 201
    assert replay.json()["id"] == order_id

    # Update catalog variant price -> historical order snapshot remains $25.00
    client.put(
        f"/api/v1/admin/variants/{variant_id}",
        json={"price": "39.00"},
        headers=ah,
    )
    hist_order = client.get(f"/api/v1/orders/{order_id}", headers=ch).json()
    assert float(hist_order["items"][0]["unit_price"]) == 25.00

    # Customer cannot set protected status via admin route
    assert (
        client.patch(
            f"/api/v1/admin/orders/{order_id}/status",
            json={"status": "DELIVERED"},
            headers=ch,
        ).status_code
        == 403
    )


def test_sandbox_payment_and_duplicate_webhook_idempotency(client, make_user):
    _c, _a, ch, ah, _p, variant_id, addr_id = _setup_catalog_and_users(client, make_user)

    today = date.today()
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-PAY-01",
            "manufacture_date": (today - timedelta(days=10)).isoformat(),
            "expiry_date": (today + timedelta(days=180)).isoformat(),
            "quantity": 3,
        },
        headers=ah,
    )
    client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 1},
        headers=ch,
    )
    order = client.post(
        "/api/v1/orders",
        json={"address_id": addr_id, "payment_method": "SANDBOX", "idempotency_key": "idem-sbx-1"},
        headers=ch,
    ).json()
    assert order["status"] == "PAYMENT_PENDING"

    pay_res = client.post(
        "/api/v1/payments",
        json={"order_id": order["id"]},
        headers=ch,
    )
    assert pay_res.status_code == 201
    payment_id = pay_res.json()["id"]

    webhook_body = {
        "provider_event_id": "evt_sandbox_unique_123",
        "payment_id": payment_id,
        "status": "PAID",
    }
    raw = json.dumps(webhook_body).encode("utf-8")
    sig = sign_webhook_payload(raw, get_settings().payment_webhook_secret)

    wh1 = client.post(
        "/api/v1/payments/webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Webhook-Signature": sig},
    )
    assert wh1.status_code == 200
    assert wh1.json()["status"] == "PAID"

    # Duplicate webhook must be idempotent and not fail or duplicate transactions
    wh2 = client.post(
        "/api/v1/payments/webhook",
        content=raw,
        headers={"Content-Type": "application/json", "X-Webhook-Signature": sig},
    )
    assert wh2.status_code == 200
    assert wh2.json()["duplicate"] is True

    pay_detail = client.get(f"/api/v1/payments/{payment_id}", headers=ch).json()
    assert len(pay_detail["transactions"]) == 1

    updated_order = client.get(f"/api/v1/orders/{order['id']}", headers=ch).json()
    assert updated_order["status"] == "PAID"
    assert updated_order["payment_status"] == "PAID"


def test_expired_batch_cannot_be_sold_and_no_overselling_last_unit(client, make_user):
    _c, _a, ch, ah, _p, variant_id, addr_id = _setup_catalog_and_users(client, make_user)
    make_user("buyer2@glowcart.com", role_name="customer")
    tok2 = client.post(
        "/api/v1/auth/login",
        json={"email": "buyer2@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    ch2 = {"Authorization": f"Bearer {tok2}"}
    addr2 = client.post(
        "/api/v1/addresses",
        json={
            "label": "Home",
            "recipient_name": "Buyer Two",
            "phone": "+1-555-0201",
            "line1": "501 Glow St",
            "city": "Los Angeles",
            "postal_code": "90001",
            "country": "USA",
            "is_default": True,
        },
        headers=ch2,
    ).json()["id"]

    today = date.today()
    # Add ONLY an expired batch first
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-EXP-ONLY",
            "manufacture_date": (today - timedelta(days=90)).isoformat(),
            "expiry_date": (today - timedelta(days=1)).isoformat(),
            "quantity": 5,
        },
        headers=ah,
    )
    cart_fail = client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 1},
        headers=ch,
    )
    assert cart_fail.status_code == 409

    # Now add 1 valid unit
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-LAST-1",
            "manufacture_date": (today - timedelta(days=10)).isoformat(),
            "expiry_date": (today + timedelta(days=120)).isoformat(),
            "quantity": 1,
        },
        headers=ah,
    )
    assert client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 1},
        headers=ch,
    ).status_code == 201
    assert client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 1},
        headers=ch2,
    ).status_code == 201

    def _checkout(headers, address_id, key):
        return client.post(
            "/api/v1/orders",
            json={"address_id": address_id, "payment_method": "COD", "idempotency_key": key},
            headers=headers,
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        f1 = pool.submit(_checkout, ch, addr_id, "conc-1")
        f2 = pool.submit(_checkout, ch2, addr2, "conc-2")
        codes = sorted([f1.result(), f2.result()])

    assert codes == [201, 409]


def test_cancel_processing_order_restores_fefo_batches_without_touching_other_reserved_stock(
    client, make_user
):
    _c, _a, ch, ah, _p, variant_id, addr_id = _setup_catalog_and_users(client, make_user)

    today = date.today()
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-RESTORE-1",
            "manufacture_date": (today - timedelta(days=10)).isoformat(),
            "expiry_date": (today + timedelta(days=180)).isoformat(),
            "quantity": 5,
        },
        headers=ah,
    )

    # Order 1: COD -> transition to PROCESSING (deducts 2 units FEFO from batch)
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 2}, headers=ch)
    order1 = client.post(
        "/api/v1/orders",
        json={"address_id": addr_id, "payment_method": "COD", "idempotency_key": "rest-1"},
        headers=ch,
    ).json()
    proc = client.patch(
        f"/api/v1/admin/orders/{order1['id']}/status",
        json={"status": "PROCESSING"},
        headers=ah,
    )
    assert proc.status_code == 200

    # Order 2: COD -> stays CONFIRMED (1 unit in reserved_quantity)
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 1}, headers=ch)
    client.post(
        "/api/v1/orders",
        json={"address_id": addr_id, "payment_method": "COD", "idempotency_key": "rest-2"},
        headers=ch,
    )

    # Admin cancels Order 1 -> must restore 2 sold units to available_quantity & batch, keeping Order 2's 1 reserved unit intact
    cancel = client.patch(
        f"/api/v1/admin/orders/{order1['id']}/status",
        json={"status": "CANCELLED"},
        headers=ah,
    )
    assert cancel.status_code == 200

    # Duplicate cancellation replay must be idempotent and not inflate inventory
    cancel_replay = client.patch(
        f"/api/v1/admin/orders/{order1['id']}/status",
        json={"status": "CANCELLED"},
        headers=ah,
    )
    assert cancel_replay.status_code == 200

    inv = client.get("/api/v1/admin/inventory", headers=ah).json()
    item = next(i for i in inv if i["variant_id"] == variant_id)
    assert item["available_quantity"] == 4
    assert item["reserved_quantity"] == 1
    assert item["sellable_quantity"] == 4


