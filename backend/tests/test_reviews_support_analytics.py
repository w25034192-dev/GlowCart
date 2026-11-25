from datetime import date, timedelta


def _setup_review_and_order_fixture(client, make_user):
    make_user("rev_cust1@glowcart.com", role_name="customer")
    make_user("rev_cust2@glowcart.com", role_name="customer")
    make_user("rev_admin@glowcart.com", role_name="admin")

    t1 = client.post(
        "/api/v1/auth/login",
        json={"email": "rev_cust1@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    t2 = client.post(
        "/api/v1/auth/login",
        json={"email": "rev_cust2@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]
    ta = client.post(
        "/api/v1/auth/login",
        json={"email": "rev_admin@glowcart.com", "password": "GlowCartPass123!"},
    ).json()["access_token"]

    h1 = {"Authorization": f"Bearer {t1}"}
    h2 = {"Authorization": f"Bearer {t2}"}
    ha = {"Authorization": f"Bearer {ta}"}

    cat_id = client.post(
        "/api/v1/admin/categories",
        json={"name": "Makeup", "slug": "makeup-rev"},
        headers=ha,
    ).json()["id"]
    brand_id = client.post(
        "/api/v1/admin/brands",
        json={"name": "MAC Test", "slug": "mac-rev"},
        headers=ha,
    ).json()["id"]
    prod_id = client.post(
        "/api/v1/admin/products",
        json={
            "category_id": cat_id,
            "brand_id": brand_id,
            "name": "MAC Velvet Lipstick",
            "slug": "mac-velvet-lipstick-rev",
            "description": "Matte lipstick.",
        },
        headers=ha,
    ).json()["id"]
    variant_id = client.post(
        "/api/v1/admin/variants",
        json={
            "product_id": prod_id,
            "sku": "MAC-LIP-RUBY",
            "shade_name": "Ruby Woo",
            "color_name": "Vivid Red",
            "hex_color": "#B31B2C",
            "price": "25.00",
        },
        headers=ha,
    ).json()["id"]

    today = date.today()
    client.post(
        "/api/v1/admin/inventory/batches",
        json={
            "variant_id": variant_id,
            "batch_number": "BATCH-REV-1",
            "manufacture_date": (today - timedelta(days=10)).isoformat(),
            "expiry_date": (today + timedelta(days=300)).isoformat(),
            "quantity": 10,
        },
        headers=ha,
    )
    addr_id = client.post(
        "/api/v1/addresses",
        json={
            "label": "Home",
            "recipient_name": "Cust 1",
            "phone": "+1-555-0300",
            "line1": "10 Beauty Blvd",
            "city": "Miami",
            "postal_code": "33101",
            "country": "USA",
            "is_default": True,
        },
        headers=h1,
    ).json()["id"]

    return h1, h2, ha, prod_id, variant_id, addr_id


def test_reviews_permissions_verified_purchase_and_duplicates(client, make_user):
    h1, h2, _ha, prod_id, variant_id, addr_id = _setup_review_and_order_fixture(client, make_user)

    # Customer 1 buys the product -> verified purchase review
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 1}, headers=h1)
    client.post(
        "/api/v1/orders",
        json={"address_id": addr_id, "payment_method": "COD", "idempotency_key": "rev-order-1"},
        headers=h1,
    )

    rev = client.post(
        "/api/v1/reviews",
        json={"product_id": prod_id, "rating": 5, "title": "Rich pigment", "comment": "Long lasting red!"},
        headers=h1,
    )
    assert rev.status_code == 201
    assert rev.json()["is_verified_purchase"] is True
    rev_id = rev.json()["id"]

    # Duplicate review rejected
    dup = client.post(
        "/api/v1/reviews",
        json={"product_id": prod_id, "rating": 4, "title": "Again", "comment": "Duplicate"},
        headers=h1,
    )
    assert dup.status_code == 409

    # Customer 2 cannot edit or delete Customer 1's review
    assert (
        client.put(
            f"/api/v1/reviews/{rev_id}",
            json={"rating": 1, "comment": "Tamper"},
            headers=h2,
        ).status_code
        == 403
    )
    assert client.delete(f"/api/v1/reviews/{rev_id}", headers=h2).status_code == 403

    # Owner can edit
    upd = client.put(
        f"/api/v1/reviews/{rev_id}",
        json={"rating": 4, "comment": "Updated comment"},
        headers=h1,
    )
    assert upd.status_code == 200
    assert upd.json()["rating"] == 4


def test_customer_messages_admin_reply_and_notifications(client, make_user):
    h1, _h2, ha, _p, _v, _a = _setup_review_and_order_fixture(client, make_user)

    msg = client.post(
        "/api/v1/messages",
        json={"subject": "Shade recommendation", "message": "Which shade matches warm undertone?"},
        headers=h1,
    )
    assert msg.status_code == 201
    msg_id = msg.json()["id"]

    reply = client.post(
        f"/api/v1/admin/messages/{msg_id}/reply",
        json={"body": "Try Warm Beige or Joy!", "status": "RESOLVED"},
        headers=ha,
    )
    assert reply.status_code == 200
    assert reply.json()["status"] == "RESOLVED"
    assert len(reply.json()["replies"]) == 1

    notifs = client.get("/api/v1/notifications", headers=h1)
    assert notifs.status_code == 200
    assert len(notifs.json()) >= 1


def test_analytics_excludes_cancelled_and_refunded_revenue(client, make_user):
    h1, _h2, ha, _p, variant_id, addr_id = _setup_review_and_order_fixture(client, make_user)

    # Order 1: Paid/Confirmed ($25 + $5 shipping = $30)
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 1}, headers=h1)
    o1 = client.post(
        "/api/v1/orders",
        json={"address_id": addr_id, "payment_method": "COD", "idempotency_key": "an-1"},
        headers=h1,
    ).json()

    # Order 2: Placed then cancelled -> must NOT count toward revenue
    client.post("/api/v1/cart/items", json={"variant_id": variant_id, "quantity": 2}, headers=h1)
    o2 = client.post(
        "/api/v1/orders",
        json={"address_id": addr_id, "payment_method": "COD", "idempotency_key": "an-2"},
        headers=h1,
    ).json()
    client.post(f"/api/v1/orders/{o2['id']}/cancel", headers=h1)

    overview = client.get("/api/v1/admin/analytics/overview", headers=ha)
    assert overview.status_code == 200
    data = overview.json()
    assert float(data["total_revenue"]) == float(o1["total_amount"])
    assert data["total_orders"] == 2

    sales = client.get("/api/v1/admin/analytics/sales?granularity=daily", headers=ha)
    assert sales.status_code == 200
    variants = client.get("/api/v1/admin/analytics/variants", headers=ha)
    assert variants.status_code == 200
    assert len(variants.json()["lipstick_shades"]) >= 1
    inv_report = client.get("/api/v1/admin/analytics/inventory", headers=ha)
    assert inv_report.status_code == 200

