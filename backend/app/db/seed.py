from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Brand,
    Cart,
    Category,
    Coupon,
    Inventory,
    InventoryBatch,
    InventoryMovement,
    Product,
    ProductImage,
    ProductVariant,
    Promotion,
    User,
    Wishlist,
)
from app.repositories.user_repository import UserRepository


CATEGORIES_DATA = [
    ("Makeup", "makeup", "Face, eye, and lip color cosmetics", 1),
    ("Skincare", "skincare", "Cleansers, toners, serums, essences, and moisturizers", 2),
    ("Sun Care", "sun-care", "Daily UV protection creams and sun sticks", 3),
    ("Hair Care", "hair-care", "Shampoos, conditioners, treatments, and hair masks", 4),
    ("Body Care", "body-care", "Body washes, lotions, scrubs, and nourishing oils", 5),
    ("Fragrance", "fragrance", "Perfumes, eau de parfum, and body mists", 6),
    ("Beauty Tools", "beauty-tools", "Brushes, sponges, and vanity tools", 7),
    ("Makeup Sets", "makeup-sets", "Curated gift sets and skincare bundles", 8),
]

BRANDS_DATA = [
    ("Maybelline", "maybelline", "USA", True),
    ("L'Oréal Paris", "loreal-paris", "France", True),
    ("MAC", "mac", "Canada", True),
    ("NYX", "nyx", "USA", False),
    ("Rare Beauty", "rare-beauty", "USA", True),
    ("Fenty Beauty", "fenty-beauty", "USA", True),
    ("Huda Beauty", "huda-beauty", "UAE", True),
    ("Charlotte Tilbury", "charlotte-tilbury", "UK", True),
    ("The Ordinary", "the-ordinary", "Canada", True),
    ("CeraVe", "cerave", "USA", True),
    ("COSRX", "cosrx", "South Korea", True),
    ("Beauty of Joseon", "beauty-of-joseon", "South Korea", True),
    ("Anua", "anua", "South Korea", False),
    ("La Roche-Posay", "la-roche-posay", "France", False),
    ("SKIN1004", "skin1004", "South Korea", False),
    ("Round Lab", "round-lab", "South Korea", False),
    ("Torriden", "torriden", "South Korea", False),
    ("Olaplex", "olaplex", "USA", False),
    ("Dior", "dior", "France", True),
    ("Sol de Janeiro", "sol-de-janeiro", "USA", False),
]

CATALOG_BLUEPRINT = [
    ("Makeup", "Maybelline", "Maybelline Fit Me Foundation", "maybelline-fit-me-foundation", ["normal", "oily", "combination"], "shades_foundation", "9.99"),
    ("Makeup", "Maybelline", "Maybelline SuperStay Matte Ink", "maybelline-superstay-matte-ink", ["all"], "shades_lip", "11.49"),
    ("Makeup", "NYX", "NYX Butter Gloss", "nyx-butter-gloss", ["all"], "shades_lip", "6.50"),
    ("Makeup", "Fenty Beauty", "Fenty Beauty Gloss Bomb", "fenty-gloss-bomb", ["all"], "shades_lip", "21.00"),
    ("Makeup", "Rare Beauty", "Rare Beauty Soft Pinch Blush", "rare-beauty-soft-pinch-blush", ["all", "dry"], "shades_blush", "23.00"),
    ("Makeup", "MAC", "MAC Studio Fix Fluid Foundation", "mac-studio-fix-fluid", ["oily", "combination"], "shades_foundation", "42.00"),
    ("Makeup", "MAC", "MAC Matte Lipstick", "mac-matte-lipstick", ["all"], "shades_lip", "23.00"),
    ("Makeup", "Huda Beauty", "Huda Beauty Easy Bake Powder", "huda-easy-bake-powder", ["oily", "combination"], "shades_powder", "38.00"),
    ("Makeup", "Charlotte Tilbury", "Charlotte Tilbury Pillow Talk Lipstick", "ct-pillow-talk-lipstick", ["all"], "shades_lip", "35.00"),
    ("Makeup", "Dior", "Dior Backstage Rosy Glow Blush", "dior-rosy-glow-blush", ["all"], "shades_blush", "40.00"),
    ("Makeup", "L'Oréal Paris", "L'Oréal True Match Concealer", "loreal-true-match-concealer", ["all"], "shades_foundation", "13.99"),
    ("Makeup", "L'Oréal Paris", "L'Oréal Lash Paradise Mascara", "loreal-lash-paradise", ["all"], "shades_eye", "12.99"),
    ("Skincare", "The Ordinary", "The Ordinary Niacinamide 10% + Zinc 1%", "ordinary-niacinamide-10", ["oily", "combination", "acne-prone"], "volumes", "6.50"),
    ("Skincare", "COSRX", "COSRX Advanced Snail 96 Mucin Essence", "cosrx-snail-96-essence", ["dry", "sensitive", "all"], "volumes", "25.00"),
    ("Skincare", "CeraVe", "CeraVe Moisturizing Cream", "cerave-moisturizing-cream", ["dry", "sensitive"], "volumes", "18.99"),
    ("Skincare", "CeraVe", "CeraVe Foaming Facial Cleanser", "cerave-foaming-cleanser", ["oily", "normal"], "volumes", "16.99"),
    ("Skincare", "Anua", "Anua Heartleaf 77% Soothing Toner", "anua-heartleaf-77-toner", ["sensitive", "acne-prone"], "volumes", "22.00"),
    ("Skincare", "SKIN1004", "SKIN1004 Madagascar Centella Ampoule", "skin1004-centella-ampoule", ["sensitive", "all"], "volumes", "19.50"),
    ("Skincare", "Round Lab", "Round Lab 1025 Dokdo Toner", "round-lab-dokdo-toner", ["sensitive", "dry", "normal"], "volumes", "18.00"),
    ("Skincare", "Torriden", "Torriden Dive-In Hyaluronic Serum", "torriden-dive-in-serum", ["dry", "dehydrated", "all"], "volumes", "24.00"),
    ("Skincare", "La Roche-Posay", "La Roche-Posay Cicaplast Baume B5", "lrp-cicaplast-b5", ["sensitive", "dry"], "volumes", "16.99"),
    ("Skincare", "The Ordinary", "The Ordinary Hyaluronic Acid 2% + B5", "ordinary-hyaluronic-b5", ["all", "dry"], "volumes", "9.90"),
    ("Skincare", "COSRX", "COSRX Low pH Good Morning Gel Cleanser", "cosrx-low-ph-cleanser", ["oily", "combination"], "volumes", "14.00"),
    ("Skincare", "Beauty of Joseon", "Beauty of Joseon Glow Serum", "boj-glow-serum", ["all", "dull"], "volumes", "17.00"),
    ("Sun Care", "Beauty of Joseon", "Beauty of Joseon Relief Sun SPF50+", "boj-relief-sun", ["all", "sensitive"], "volumes", "18.00"),
    ("Sun Care", "Beauty of Joseon", "Beauty of Joseon Matte Sun Stick", "boj-matte-sun-stick", ["oily", "combination"], "sizes", "18.00"),
    ("Sun Care", "La Roche-Posay", "La Roche-Posay Anthelios Invisible Fluid", "lrp-anthelios-fluid", ["sensitive", "all"], "volumes", "33.50"),
    ("Sun Care", "SKIN1004", "SKIN1004 Hyalu-Cica Water-Fit Sun Serum", "skin1004-sun-serum", ["dry", "all"], "volumes", "16.50"),
    ("Sun Care", "Round Lab", "Round Lab Birch Juice Moisturizing Sun Cream", "round-lab-birch-sun", ["dry", "normal"], "volumes", "21.00"),
    ("Hair Care", "Olaplex", "Olaplex No. 3 Hair Perfector", "olaplex-no-3", ["all"], "volumes", "30.00"),
    ("Hair Care", "Olaplex", "Olaplex No. 4 Bond Maintenance Shampoo", "olaplex-no-4-shampoo", ["all"], "volumes", "30.00"),
    ("Hair Care", "Olaplex", "Olaplex No. 5 Bond Maintenance Conditioner", "olaplex-no-5-conditioner", ["all"], "volumes", "30.00"),
    ("Hair Care", "Olaplex", "Olaplex No. 7 Bonding Oil", "olaplex-no-7-oil", ["all"], "volumes", "30.00"),
    ("Hair Care", "L'Oréal Paris", "L'Oréal Elvive Hyaluron Plump Serum", "loreal-hyaluron-hair-serum", ["all"], "volumes", "11.99"),
    ("Body Care", "Sol de Janeiro", "Sol de Janeiro Brazilian Bum Bum Cream", "sdj-bum-bum-cream", ["all", "dry"], "volumes", "22.00"),
    ("Body Care", "Sol de Janeiro", "Sol de Janeiro Delicia Drench Body Butter", "sdj-delicia-body-butter", ["dry"], "volumes", "24.00"),
    ("Body Care", "CeraVe", "CeraVe SA Smoothing Body Wash", "cerave-sa-body-wash", ["rough", "all"], "volumes", "15.99"),
    ("Body Care", "La Roche-Posay", "La Roche-Posay Lipikar Body Balm", "lrp-lipikar-balm", ["dry", "sensitive"], "volumes", "20.99"),
    ("Fragrance", "Dior", "Miss Dior Blooming Bouquet Eau de Toilette", "miss-dior-blooming-bouquet", ["all"], "volumes", "95.00"),
    ("Fragrance", "Sol de Janeiro", "Sol de Janeiro Cheirosa 62 Perfume Mist", "sdj-cheirosa-62-mist", ["all"], "volumes", "24.00"),
    ("Fragrance", "Sol de Janeiro", "Sol de Janeiro Cheirosa 68 Perfume Mist", "sdj-cheirosa-68-mist", ["all"], "volumes", "24.00"),
    ("Fragrance", "Charlotte Tilbury", "Charlotte Tilbury Calm Bliss Fragrance", "ct-calm-bliss", ["all"], "volumes", "65.00"),
    ("Beauty Tools", "Rare Beauty", "Rare Beauty Liquid Blush Brush", "rare-beauty-blush-brush", ["all"], "sizes", "23.00"),
    ("Beauty Tools", "NYX", "NYX Marshmellow Blending Sponge", "nyx-blending-sponge", ["all"], "sizes", "9.00"),
    ("Beauty Tools", "Fenty Beauty", "Fenty Beauty Precision Makeup Sponge", "fenty-makeup-sponge", ["all"], "sizes", "16.00"),
    ("Beauty Tools", "MAC", "MAC 217S Blending Brush", "mac-217s-brush", ["all"], "sizes", "28.00"),
    ("Makeup Sets", "Rare Beauty", "Rare Beauty Pinch & Glow Mini Set", "rare-beauty-pinch-glow-set", ["all"], "sizes", "32.00"),
    ("Makeup Sets", "Fenty Beauty", "Fenty Beauty Glossy Posse Trio Set", "fenty-glossy-posse-set", ["all"], "sizes", "42.00"),
    ("Makeup Sets", "COSRX", "COSRX Snail Glass Skin Starter Kit", "cosrx-glass-skin-kit", ["dry", "all"], "sizes", "38.00"),
    ("Makeup Sets", "Beauty of Joseon", "Beauty of Joseon Hanbang Discovery Bundle", "boj-hanbang-bundle", ["all", "sensitive"], "sizes", "45.00"),
]

VARIANT_TEMPLATES = {
    "shades_foundation": [
        ("Porcelain", "110", "Fair Neutral", "#F7E5D6", None),
        ("Ivory", "120", "Light Warm", "#F2D5BE", None),
        ("Natural Beige", "220", "Medium Neutral", "#DFB391", None),
        ("Warm Beige", "240", "Medium Warm", "#D19E76", None),
    ],
    "shades_lip": [
        ("Classic Red", "RD01", "Crimson Red", "#B31B2C", None),
        ("Soft Pink", "PK02", "Rosewood Pink", "#D67B88", None),
        ("Warm Nude", "ND03", "Caramel Nude", "#B97D67", None),
    ],
    "shades_blush": [
        ("Joy", "BL01", "Muted Peach", "#E47A68", None),
        ("Hope", "BL02", "Nude Mauve", "#C97A7E", None),
    ],
    "shades_powder": [
        ("Sugar Cookie", "PW01", "Translucent Fair", "#FAF3EC", None),
        ("Banana Bread", "PW02", "Warm Golden", "#EAD2AC", None),
    ],
    "shades_eye": [
        ("Jet Black", "BK01", "Deep Black", "#1C1B1B", None),
        ("Espresso Brown", "BR02", "Soft Brown", "#4E3629", None),
    ],
    "volumes": [
        (None, None, None, None, 30),
        (None, None, None, None, 50),
    ],
    "sizes": [
        (None, None, None, None, None),
        (None, None, None, None, None),
    ],
}


def seed_demo_data(db: Session) -> None:
    roles = UserRepository(db).ensure_default_roles()

    # Demo users (Customer, Admin, Super Admin)
    demo_users = [
        ("customer@glowcart.com", "Clara Demo Customer", "customer", "GlowCartDemo123!"),
        ("admin@glowcart.com", "Aria Store Admin", "admin", "GlowCartAdmin123!"),
        ("superadmin@glowcart.com", "Elena Super Admin", "super_admin", "GlowCartSuper123!"),
    ]
    for email, name, role_name, pwd in demo_users:
        if db.query(User).filter(User.email == email).first() is None:
            u = User(
                role_id=roles[role_name].id,
                email=email,
                full_name=name,
                password_hash=hash_password(pwd),
                is_active=True,
            )
            db.add(u)
            db.flush()
            db.add(Cart(user_id=u.id))
            db.add(Wishlist(user_id=u.id))

    # Categories
    cat_map: dict[str, Category] = {}
    for name, slug, desc, order in CATEGORIES_DATA:
        cat = db.query(Category).filter(Category.slug == slug).first()
        if cat is None:
            cat = Category(name=name, slug=slug, description=desc, sort_order=order)
            db.add(cat)
            db.flush()
        cat_map[name] = cat

    # Brands
    brand_map: dict[str, Brand] = {}
    for name, slug, country, featured in BRANDS_DATA:
        brand = db.query(Brand).filter(Brand.slug == slug).first()
        if brand is None:
            brand = Brand(
                name=name,
                slug=slug,
                country_of_origin=country,
                is_featured=featured,
                description=f"Demo brand catalog entry for {name}.",
            )
            db.add(brand)
            db.flush()
        brand_map[name] = brand

    # Products (>=50) & Variants (>=100) + Batches
    today = date.today()
    for idx, (cat_name, brand_name, prod_name, slug, skins, tpl_key, base_price_str) in enumerate(
        CATALOG_BLUEPRINT, start=1
    ):
        product = db.query(Product).filter(Product.slug == slug).first()
        if product is not None:
            continue
        base_price = Decimal(base_price_str)
        product = Product(
            category_id=cat_map[cat_name].id,
            brand_id=brand_map[brand_name].id,
            name=prod_name,
            slug=slug,
            short_description=f"Illustrative demo cosmetic entry — {prod_name}.",
            description=f"{prod_name} by {brand_name}. Demo catalog description with illustrative USD pricing for GlowCart.",
            skin_types=skins,
            specifications={"origin": brand_map[brand_name].country_of_origin or "International", "demo_notice": "Illustrative demo data"},
            verified_ingredients=None,
            is_featured=(idx <= 10),
            is_new_arrival=(idx % 3 == 0),
            is_best_seller=(idx % 2 == 0),
            is_demo=True,
        )
        db.add(product)
        db.flush()

        db.add(
            ProductImage(
                product_id=product.id,
                image_url=f"https://placehold.co/600x600/FAF8F6/8F2D46?text={slug.replace('-', '+')}",
                alt_text=prod_name,
                is_primary=True,
                sort_order=0,
            )
        )

        variants_spec = VARIANT_TEMPLATES[tpl_key]
        for v_idx, (shade_name, shade_code, color_name, hex_color, vol_ml) in enumerate(
            variants_spec, start=1
        ):
            sku = f"GC-{idx:03d}-{v_idx:02d}"
            price = base_price + Decimal(str((v_idx - 1) * 4)) if vol_ml else base_price
            orig = (price + Decimal("4.00")) if idx % 4 == 0 else None
            size_label = (
                "Standard" if tpl_key == "sizes" and v_idx == 1 else ("Deluxe" if tpl_key == "sizes" else None)
            )
            variant = ProductVariant(
                product_id=product.id,
                sku=sku,
                shade_name=shade_name,
                shade_code=shade_code,
                color_name=color_name,
                hex_color=hex_color,
                volume_ml=vol_ml,
                size=size_label,
                price=price,
                original_price=orig,
                is_available=True,
                status="ACTIVE",
            )
            db.add(variant)
            db.flush()

            qty = 25 if idx % 7 != 0 else 4
            db.add(
                Inventory(
                    variant_id=variant.id,
                    available_quantity=qty,
                    reserved_quantity=0,
                    low_stock_threshold=8,
                )
            )
            batch = InventoryBatch(
                variant_id=variant.id,
                batch_number=f"DEMO-{idx:03d}-{v_idx:02d}",
                manufacture_date=today - timedelta(days=60),
                expiry_date=today + timedelta(days=365 if idx % 6 != 0 else 35),
                initial_quantity=qty,
                remaining_quantity=qty,
                received_date=today - timedelta(days=30),
            )
            db.add(batch)
            db.flush()
            db.add(
                InventoryMovement(
                    variant_id=variant.id,
                    batch_id=batch.id,
                    movement_type="RECEIVED",
                    quantity_delta=qty,
                    reference_type="demo_seed",
                    reference_id=batch.batch_number,
                    reason="Initial illustrative demo catalog stock",
                )
            )

    # Demo Promotion & Coupon
    now = datetime.now(timezone.utc)
    if db.query(Promotion).count() == 0:
        promo = Promotion(
            title="Autumn Glow Welcome Event (Demo)",
            description="Enjoy 15% off illustrative demo beauty favorites.",
            discount_type="PERCENTAGE",
            discount_value=Decimal("15.00"),
            starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=90),
            is_active=True,
        )
        db.add(promo)
        db.flush()
        db.add(
            Coupon(
                promotion_id=promo.id,
                code="GLOW15",
                discount_type="PERCENTAGE",
                discount_value=Decimal("15.00"),
                min_order_amount=Decimal("20.00"),
                max_uses=1000,
                expires_at=now + timedelta(days=90),
                is_active=True,
            )
        )

    db.commit()


if __name__ == "__main__":
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        seed_demo_data(session)
        print("GlowCart demo data seeded successfully.")
