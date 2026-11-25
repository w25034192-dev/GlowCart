from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import func
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
    Role,
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
    # Popular Local Brands (Myanmar)
    ("Shwe Pyi Nann", "shwe-pyi-nann", "Myanmar", True),
    ("Bella Cosmetics", "bella-cosmetics", "Myanmar", True),
    ("Bell", "bell", "Myanmar", True),
    ("Heritage Herbal", "heritage-herbal", "Myanmar", True),
    # Top Global Popular Brands
    ("Laneige", "laneige", "South Korea", True),
    ("Innisfree", "innisfree", "South Korea", True),
    ("NARS", "nars", "France", True),
    ("Yves Saint Laurent", "ysl", "France", True),
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
    # --- Authentic Popular Local Cosmetics & Skincare (Myanmar) ---
    ("Skincare", "Shwe Pyi Nann", "Shwe Pyi Nann Natural Bark Thanakha Pudding Face Pack", "shwe-pyi-nann-thanakha-pudding", ["all", "oily", "acne-prone"], "volumes", "12.50"),
    ("Skincare", "Shwe Pyi Nann", "Shwe Pyi Nann Lime Natural Thanakha Purifying Cream", "shwe-pyi-nann-lime-thanakha", ["oily", "combination", "acne-prone"], "volumes", "9.50"),
    ("Sun Care", "Shwe Pyi Nann", "Shwe Pyi Nann Herbal Natural UV Protection Thanakha", "shwe-pyi-nann-sun-shield", ["all", "sensitive"], "sizes", "11.00"),
    ("Body Care", "Shwe Pyi Nann", "Shwe Pyi Nann Golden Thanakha Nourishing Body Lotion", "shwe-pyi-nann-body-lotion", ["all", "dry"], "volumes", "13.50"),
    ("Makeup", "Bella Cosmetics", "Bella Matte Velvet Lip Crayon", "bella-matte-velvet-lip-crayon", ["all"], "shades_lip", "8.50"),
    ("Makeup", "Bella Cosmetics", "Bella Glow Cushion Foundation SPF50+", "bella-glow-cushion-foundation", ["normal", "combination"], "shades_foundation", "14.99"),
    ("Makeup", "Bella Cosmetics", "Bella Ultra Fine HD Translucent Powder", "bella-ultra-fine-hd-powder", ["oily", "combination"], "shades_powder", "10.00"),
    ("Makeup", "Bell", "Bell Silk Matte Oil-Control Compact Powder", "bell-silk-matte-compact-powder", ["all", "oily"], "shades_powder", "7.50"),
    ("Hair Care", "Heritage Herbal", "Tayaw Kinpun Natural Herbal Hair Shampoo & Cleanser", "tayaw-kinpun-herbal-shampoo", ["all"], "volumes", "12.00"),
    ("Fragrance", "Heritage Herbal", "Royal Inle Jasmine & Sandalwood Botanical Body Mist", "royal-inle-jasmine-mist", ["all"], "volumes", "22.00"),
    ("Beauty Tools", "Bell", "Bell Flawless Teardrop Velvet Beauty Sponge", "bell-flawless-beauty-sponge", ["all"], "sizes", "5.50"),
    ("Makeup Sets", "Bella Cosmetics", "Bella Iconic Yangon Glam Beauty Starter Set", "bella-yangon-glam-set", ["all"], "sizes", "28.00"),
    # --- Top Global Popular Cosmetic Cult Favorites ---
    ("Skincare", "Laneige", "Laneige Lip Sleeping Mask Intense Hydration", "laneige-lip-sleeping-mask", ["all", "dry"], "sizes", "24.00"),
    ("Skincare", "Laneige", "Laneige Water Bank Blue Hyaluronic Moisture Cream", "laneige-water-bank-cream", ["dry", "dehydrated", "sensitive"], "volumes", "40.00"),
    ("Skincare", "Innisfree", "Innisfree Green Tea Seed Hyaluronic Serum", "innisfree-green-tea-serum", ["all", "combination"], "volumes", "30.00"),
    ("Sun Care", "Innisfree", "Innisfree Daily UV Defense Sunscreen Broad Spectrum SPF36", "innisfree-daily-uv-defense", ["all"], "volumes", "18.00"),
    ("Makeup", "NARS", "NARS Radiant Creamy Concealer", "nars-radiant-creamy-concealer", ["all"], "shades_foundation", "32.00"),
    ("Makeup", "NARS", "NARS Orgasm Powder Blush", "nars-orgasm-powder-blush", ["all"], "shades_blush", "34.00"),
    ("Makeup", "Yves Saint Laurent", "YSL Rouge Pur Couture The Slim Velvet Radical Lipstick", "ysl-rouge-pur-couture-slim", ["all"], "shades_lip", "45.00"),
    ("Fragrance", "Yves Saint Laurent", "YSL Libre Eau De Parfum", "ysl-libre-eau-de-parfum", ["all"], "volumes", "98.00"),
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


def ensure_default_admin_and_roles(db: Session) -> dict[str, Role]:
    """Ensure base RBAC roles and at least one default admin/super_admin exist."""
    roles = UserRepository(db).ensure_default_roles()

    has_admin = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(Role.name.in_(["admin", "super_admin"]))
        .first()
        is not None
    )
    if not has_admin:
        default_admins = [
            ("admin@glowcart.com", "Aria Store Admin", "admin", "GlowCartAdmin123!"),
            ("superadmin@glowcart.com", "Elena Super Admin", "super_admin", "GlowCartSuper123!"),
        ]
        for email, name, role_name, pwd in default_admins:
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
        db.commit()
    return roles


def _ensure_categories_and_brands(db: Session) -> tuple[dict[str, Category], dict[str, Brand]]:
    """Ensure canonical categories and brands exist and are active without duplicating existing records."""
    cat_map: dict[str, Category] = {}
    for name, slug, desc, order in CATEGORIES_DATA:
        cat = (
            db.query(Category)
            .filter(
                (func.lower(Category.slug) == slug) | (func.lower(Category.name) == name.lower())
            )
            .first()
        )
        if cat is None:
            cat = Category(name=name, slug=slug, description=desc, sort_order=order, is_active=True)
            db.add(cat)
            db.flush()
        else:
            if not cat.is_active:
                cat.is_active = True
            if cat.slug != slug and db.query(Category).filter(Category.slug == slug).first() is None:
                cat.slug = slug
        cat_map[name] = cat

    brand_map: dict[str, Brand] = {}
    for name, slug, country, featured in BRANDS_DATA:
        brand = (
            db.query(Brand)
            .filter((func.lower(Brand.slug) == slug) | (func.lower(Brand.name) == name.lower()))
            .first()
        )
        if brand is None:
            brand = Brand(
                name=name,
                slug=slug,
                country_of_origin=country,
                is_featured=featured,
                is_active=True,
                description=f"Demo brand catalog entry for {name}.",
            )
            db.add(brand)
            db.flush()
        else:
            if not brand.is_active:
                brand.is_active = True
        brand_map[name] = brand

    return cat_map, brand_map


REAL_COSMETIC_IMAGES = {
    "shwe-pyi-nann-thanakha-pudding": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80",
    "shwe-pyi-nann-lime-thanakha": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80",
    "shwe-pyi-nann-sun-shield": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=800&q=80",
    "shwe-pyi-nann-body-lotion": "https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=800&q=80",
    "bella-matte-velvet-lip-crayon": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80",
    "bella-glow-cushion-foundation": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80",
    "bella-ultra-fine-hd-powder": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
    "bell-silk-matte-compact-powder": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
    "tayaw-kinpun-herbal-shampoo": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=800&q=80",
    "royal-inle-jasmine-mist": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=800&q=80",
    "bell-flawless-beauty-sponge": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
    "bella-yangon-glam-set": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
    "laneige-lip-sleeping-mask": "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80",
    "laneige-water-bank-cream": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80",
    "innisfree-green-tea-serum": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
    "innisfree-daily-uv-defense": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=800&q=80",
    "nars-radiant-creamy-concealer": "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
    "nars-orgasm-powder-blush": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80",
    "ysl-rouge-pur-couture-slim": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80",
    "ysl-libre-eau-de-parfum": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80",
}

CATEGORY_REAL_IMAGES = {
    "Makeup": {
        "foundation": "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "concealer": "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "lip": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80",
        "gloss": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80",
        "blush": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80",
        "powder": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
        "mascara": "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80",
    },
    "Skincare": {
        "serum": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
        "ampoule": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
        "cream": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80",
        "baume": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80",
        "toner": "https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80",
        "essence": "https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80",
        "cleanser": "https://images.unsplash.com/photo-1556228722-d0b5eb1c11d5?auto=format&fit=crop&w=800&q=80",
        "thanakha": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
    },
    "Sun Care": {
        "stick": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1567928815116-3e33b006c6e7?auto=format&fit=crop&w=800&q=80",
    },
    "Hair Care": {
        "oil": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80",
        "shampoo": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=800&q=80",
        "conditioner": "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80",
    },
    "Body Care": {
        "lotion": "https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=800&q=80",
        "butter": "https://images.unsplash.com/photo-1556228722-d0b5eb1c11d5?auto=format&fit=crop&w=800&q=80",
        "wash": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=800&q=80",
    },
    "Fragrance": {
        "mist": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80",
    },
    "Beauty Tools": {
        "brush": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80",
        "sponge": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80",
    },
    "Makeup Sets": {
        "kit": "https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80",
        "default": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
    },
}


def resolve_seed_image_url(cat_name: str, prod_name: str, slug: str) -> str:
    """Return high-resolution realistic cosmetic photograph URL matching the product item."""
    if slug in REAL_COSMETIC_IMAGES:
        return REAL_COSMETIC_IMAGES[slug]
    cat_rules = CATEGORY_REAL_IMAGES.get(cat_name, {})
    lower_name = prod_name.lower()
    for keyword, url in cat_rules.items():
        if keyword != "default" and keyword in lower_name:
            return url
    return cat_rules.get("default", "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80")


def _seed_blueprint_entries(
    db: Session,
    indexed_entries: list[tuple[int, tuple]],
    cat_map: dict[str, Category],
    brand_map: dict[str, Brand],
) -> int:
    """Insert missing products, variants, images, and initial batches without duplicating existing slugs."""
    today = date.today()
    created_count = 0
    for idx, (cat_name, brand_name, prod_name, slug, skins, tpl_key, base_price_str) in indexed_entries:
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
            specifications={
                "origin": brand_map[brand_name].country_of_origin or "International",
                "demo_notice": "Illustrative demo data",
            },
            verified_ingredients=None,
            is_featured=(idx <= 10),
            is_new_arrival=(idx % 3 == 0),
            is_best_seller=(idx % 2 == 0),
            is_demo=True,
        )
        db.add(product)
        db.flush()
        created_count += 1

        db.add(
            ProductImage(
                product_id=product.id,
                image_url=resolve_seed_image_url(cat_name, prod_name, slug),
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
    return created_count


def seed_demo_data(db: Session) -> None:
    roles = ensure_default_admin_and_roles(db)

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

    cat_map, brand_map = _ensure_categories_and_brands(db)
    _seed_blueprint_entries(db, list(enumerate(CATALOG_BLUEPRINT, start=1)), cat_map, brand_map)

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


def ensure_initial_data(db: Session) -> bool:
    """Ensure default admin exists and ensure all canonical categories, brands, and catalog items exist with real images."""
    ensure_default_admin_and_roles(db)
    cat_map, brand_map = _ensure_categories_and_brands(db)
    all_blueprint_entries = list(enumerate(CATALOG_BLUEPRINT, start=1))
    created = _seed_blueprint_entries(db, all_blueprint_entries, cat_map, brand_map)

    # Upgrade any existing product images pointing to generic SVG placeholders to real photographs
    updated_images = 0
    for img in db.query(ProductImage).all():
        if img.image_url and img.image_url.endswith(".svg"):
            prod = db.query(Product).filter(Product.id == img.product_id).first()
            if prod and prod.category:
                img.image_url = resolve_seed_image_url(prod.category.name, prod.name, prod.slug)
                updated_images += 1

    if created > 0 or updated_images > 0:
        db.commit()
        return True
    return False


if __name__ == "__main__":
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        seed_demo_data(session)
        print("GlowCart demo data seeded successfully.")
