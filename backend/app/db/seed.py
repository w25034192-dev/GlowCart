from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import random
import re
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
    ("Estée Lauder", "estee-lauder", "USA", True),
    ("Rom&nd", "romand", "South Korea", True),
    ("Medicube", "medicube", "South Korea", True),
    # Studio Atelier Brands
    ("Atelier Lab", "atelier-lab", "France", True),
    ("GlowCart Studio", "glowcart-studio", "International", True),
    ("Solis Botanica", "solis-botanica", "USA", True),
    ("KeraFlora", "keraflora", "South Korea", True),
    ("Velvet Veil", "velvet-veil", "UK", True),
    ("Lumière Skin", "lumiere-skin", "France", True),
]

CATALOG_BLUEPRINT = [
    # --- Makeup Popular Products (Fit Me, Centella, Dior, Rare Beauty, etc.) ---
    ("Makeup", "Maybelline", "Maybelline Fit Me Matte + Poreless Liquid Foundation", "maybelline-fit-me-foundation", ["oily", "combination"], "volumes", "30ml", "10.99"),
    ("Makeup", "Maybelline", "Maybelline Fit Me Concealer", "maybelline-fit-me-concealer", ["all"], "volumes", "6.8ml", "8.99"),
    ("Makeup", "Maybelline", "Maybelline Fit Me Loose Finishing Powder", "maybelline-fit-me-loose-powder", ["oily", "combination"], "sizes", "20g", "9.99"),
    ("Makeup", "Maybelline", "Maybelline Lash Sensational Sky High Mascara", "maybelline-sky-high-mascara", ["all"], "volumes", "7.2ml", "12.99"),
    ("Makeup", "SKIN1004", "SKIN1004 Madagascar Centella Tone-Up Cushion SPF50+", "skin1004-centella-toneup-cushion", ["sensitive", "all"], "sizes", "15g", "22.00"),
    ("Makeup", "Dior", "Dior Forever Skin Glow Foundation", "dior-forever-skin-glow-foundation", ["dry", "normal"], "volumes", "30ml", "57.00"),
    ("Makeup", "Dior", "Dior Addict Lip Glow Oil", "dior-addict-lip-glow-oil", ["all"], "shades_lip", "6ml", "40.00"),
    ("Makeup", "Rare Beauty", "Rare Beauty Soft Pinch Liquid Blush", "rare-beauty-soft-pinch-blush", ["all"], "volumes", "7.5ml", "23.00"),
    ("Makeup", "Charlotte Tilbury", "Charlotte Tilbury Pillow Talk Matte Revolution Lipstick", "ct-pillow-talk-lipstick", ["all"], "shades_lip", "3.5g", "35.00"),
    ("Makeup", "NARS", "NARS Radiant Creamy Concealer", "nars-radiant-creamy-concealer", ["all"], "volumes", "6ml", "32.00"),
    ("Makeup", "Estée Lauder", "Estée Lauder Double Wear Stay-in-Place Foundation", "estee-lauder-double-wear", ["oily", "combination"], "volumes", "30ml", "52.00"),
    ("Makeup", "Rom&nd", "Rom&nd Juicy Lasting Tint", "romand-juicy-lasting-tint", ["all"], "shades_lip", "5.5g", "11.50"),
    ("Makeup", "MAC", "MAC Retro Matte Lipstick Ruby Woo", "mac-retro-matte-ruby-woo", ["all"], "shades_lip", "3g", "23.00"),
    ("Makeup", "Fenty Beauty", "Fenty Beauty Gloss Bomb Universal Lip Luminizer", "fenty-gloss-bomb-luminizer", ["all"], "shades_lip", "9ml", "21.00"),
    ("Makeup", "Laneige", "Laneige Neo Cushion Matte SPF42", "laneige-neo-cushion-matte", ["oily", "combination"], "sizes", "15g", "34.00"),

    # --- Skincare Popular Products (The Ordinary, CeraVe, Medicube, Centella, etc.) ---
    ("Skincare", "The Ordinary", "The Ordinary Niacinamide 10% + Zinc 1% Serum", "the-ordinary-niacinamide-10-zinc-1", ["oily", "combination"], "volumes", "30ml", "6.50"),
    ("Skincare", "The Ordinary", "The Ordinary Hyaluronic Acid 2% + B5 Hydrating Serum", "the-ordinary-hyaluronic-acid-2-b5", ["dry", "all"], "volumes", "30ml", "9.90"),
    ("Skincare", "The Ordinary", "The Ordinary Glycolic Acid 7% Exfoliating Toning Solution", "the-ordinary-glycolic-acid-7-toner", ["oily", "combination"], "volumes", "240ml", "13.00"),
    ("Skincare", "The Ordinary", "The Ordinary AHA 30% + BHA 2% Peeling Solution", "the-ordinary-aha-30-bha-2-peeling", ["oily", "combination"], "volumes", "30ml", "9.50"),
    ("Skincare", "CeraVe", "CeraVe Hydrating Facial Cleanser", "cerave-hydrating-facial-cleanser", ["dry", "sensitive"], "volumes", "236ml", "15.99"),
    ("Skincare", "CeraVe", "CeraVe Foaming Facial Cleanser", "cerave-foaming-facial-cleanser", ["oily", "combination"], "volumes", "236ml", "15.99"),
    ("Skincare", "CeraVe", "CeraVe Daily Moisturizing Lotion", "cerave-daily-moisturizing-lotion", ["dry", "all"], "volumes", "355ml", "16.49"),
    ("Skincare", "CeraVe", "CeraVe PM Facial Moisturizing Lotion", "cerave-pm-facial-lotion", ["all", "sensitive"], "volumes", "89ml", "17.99"),
    ("Skincare", "Medicube", "Medicube Zero Pore Pad 2.0", "medicube-zero-pore-pad-2", ["oily", "combination"], "sizes", "70 pads", "24.00"),
    ("Skincare", "Medicube", "Medicube Collagen Night Wrapping Mask", "medicube-collagen-night-mask", ["dry", "all"], "volumes", "75ml", "28.00"),
    ("Skincare", "Medicube", "Medicube PDRN Pink Peptide Serum", "medicube-pdrn-pink-peptide-serum", ["all", "dry"], "volumes", "30ml", "25.00"),
    ("Skincare", "SKIN1004", "SKIN1004 Madagascar Centella Ampoule", "skin1004-madagascar-centella-ampoule", ["sensitive", "all"], "volumes", "55ml", "18.50"),
    ("Skincare", "SKIN1004", "SKIN1004 Madagascar Centella Toning Toner", "skin1004-centella-toning-toner", ["sensitive", "combination"], "volumes", "210ml", "19.00"),
    ("Skincare", "Anua", "Anua Heartleaf 77% Soothing Toner", "anua-heartleaf-77-soothing-toner", ["sensitive", "oily"], "volumes", "250ml", "23.00"),
    ("Skincare", "COSRX", "COSRX Advanced Snail 96 Mucin Power Essence", "cosrx-advanced-snail-96-essence", ["dry", "sensitive"], "volumes", "100ml", "21.00"),
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
    ("Makeup", "NARS", "NARS Orgasm Powder Blush", "nars-orgasm-powder-blush", ["all"], "shades_blush", "34.00"),
    ("Makeup", "Yves Saint Laurent", "YSL Rouge Pur Couture The Slim Velvet Radical Lipstick", "ysl-rouge-pur-couture-slim", ["all"], "shades_lip", "45.00"),
    ("Fragrance", "Yves Saint Laurent", "YSL Libre Eau De Parfum", "ysl-libre-eau-de-parfum", ["all"], "volumes", "98.00"),

    # --- Batch 3: 30 New Products (Sun Care / Hair Care / Fragrance / Body Care / Skincare / Makeup) ---

    # Sun Care (6)
    ("Sun Care", "Beauty of Joseon", "Beauty of Joseon Relief Sun Rice + Probiotics SPF50+ PA++++", "boj-relief-sun-rice-probiotics", ["sensitive", "all"], "volumes", "50ml", "15.00"),
    ("Sun Care", "COSRX", "COSRX Aloe Soothing Sun Cream SPF50+ PA+++", "cosrx-aloe-sun-cream-spf50", ["sensitive", "dry"], "volumes", "50ml", "14.00"),
    ("Sun Care", "La Roche-Posay", "La Roche-Posay Anthelios Invisible Fluid SPF50+", "lrp-anthelios-invisible-fluid-spf50", ["all", "oily"], "volumes", "50ml", "29.00"),
    ("Sun Care", "Anua", "Anua Heartleaf Calming Sun Serum SPF50+ PA++++", "anua-heartleaf-sun-serum-spf50", ["sensitive", "acne-prone"], "volumes", "50ml", "18.00"),
    ("Sun Care", "Round Lab", "Round Lab Birch Juice Moisturizing Sun Cream SPF50+ PA++++", "round-lab-birch-sun-cream-spf50", ["dry", "sensitive"], "volumes", "50ml", "16.00"),
    ("Sun Care", "Torriden", "Torriden Dive-In Sun Serum SPF50+ PA++++", "torriden-dive-in-sun-serum-spf50", ["dry", "dehydrated"], "volumes", "50ml", "17.00"),

    # Hair Care (6)
    ("Hair Care", "Olaplex", "Olaplex No. 3 Hair Perfector Bond Repair Treatment", "olaplex-no3-hair-perfector", ["all"], "volumes", "100ml", "30.00"),
    ("Hair Care", "Olaplex", "Olaplex No. 8 Bond Intense Moisture Mask", "olaplex-no8-moisture-mask", ["all"], "volumes", "100ml", "32.00"),
    ("Hair Care", "L'Oréal Paris", "L'Oréal Paris Elvive Extraordinary Oil Hair Serum", "loreal-elvive-extraordinary-oil-serum", ["all"], "volumes", "100ml", "12.00"),
    ("Hair Care", "L'Oréal Paris", "L'Oréal Paris EverPure Sulfate Free Color Care Shampoo", "loreal-everpure-color-shampoo", ["all"], "volumes", "250ml", "9.99"),
    ("Hair Care", "COSRX", "COSRX Full Fit Propolis Nourishing Hair Ampoule", "cosrx-propolis-hair-ampoule", ["dry", "damaged"], "volumes", "100ml", "22.00"),
    ("Hair Care", "Innisfree", "Innisfree My Hair Recipe Moisture Treatment", "innisfree-hair-recipe-moisture", ["dry", "all"], "volumes", "150ml", "14.00"),

    # Fragrance (5)
    ("Fragrance", "Sol de Janeiro", "Sol de Janeiro Cheirosa 71 Perfume Mist", "sdj-cheirosa-71-mist", ["all"], "volumes", "240ml", "36.00"),
    ("Fragrance", "Sol de Janeiro", "Sol de Janeiro Bum Bum Body Lotion Limited Edition Mist", "sdj-bum-bum-mist-lotion", ["all"], "volumes", "240ml", "26.00"),
    ("Fragrance", "Dior", "Dior Sauvage Eau de Parfum", "dior-sauvage-eau-de-parfum", ["all"], "volumes", "100ml", "120.00"),
    ("Fragrance", "Innisfree", "Innisfree Jeju Blossom Eau de Toilette", "innisfree-jeju-blossom-edt", ["all"], "volumes", "50ml", "28.00"),
    ("Fragrance", "Estée Lauder", "Estée Lauder Beautiful Magnolia Eau de Parfum", "estee-lauder-beautiful-magnolia-edp", ["all"], "volumes", "50ml", "95.00"),

    # Body Care (5)
    ("Body Care", "Sol de Janeiro", "Sol de Janeiro Brazilian Bum Bum Cream 240ml XL Edition", "sdj-bum-bum-cream-240ml", ["all"], "volumes", "240ml", "52.00"),
    ("Body Care", "CeraVe", "CeraVe Moisturizing Cream Body & Face", "cerave-moisturizing-cream-body-face", ["dry", "sensitive"], "volumes", "454g", "19.99"),
    ("Body Care", "La Roche-Posay", "La Roche-Posay Lipikar Syndet AP+ Wash Cream", "lrp-lipikar-syndet-ap-wash", ["dry", "sensitive", "eczema"], "volumes", "400ml", "24.00"),
    ("Body Care", "COSRX", "COSRX Advanced Snail 92 All In One Cream Body", "cosrx-snail-92-body-cream", ["all", "dry"], "volumes", "200ml", "21.00"),
    ("Body Care", "Anua", "Anua Peach 70% Niacin Peptide Moisture Body Lotion", "anua-peach-niacin-body-lotion", ["all", "dry"], "volumes", "200ml", "19.00"),

    # Skincare (4)
    ("Skincare", "COSRX", "COSRX Propolis Light Ampule 70%", "cosrx-propolis-light-ampule-70", ["all", "combination"], "volumes", "35ml", "24.00"),
    ("Skincare", "Beauty of Joseon", "Beauty of Joseon Revive Eye Serum Ginseng + Retinal", "boj-revive-eye-serum-ginseng-retinal", ["all", "mature"], "volumes", "30ml", "22.00"),
    ("Skincare", "Torriden", "Torriden Dive-In Low Molecular Hyaluronic Acid Serum", "torriden-dive-in-ha-serum", ["dry", "dehydrated", "all"], "volumes", "50ml", "20.00"),
    ("Skincare", "Round Lab", "Round Lab 1025 Dokdo Toner Pore Minimizing Calming", "round-lab-dokdo-toner", ["oily", "sensitive", "combination"], "volumes", "200ml", "18.00"),

    # Makeup (4)
    ("Makeup", "Fenty Beauty", "Fenty Beauty Pro Filt'r Soft Matte Longwear Foundation", "fenty-pro-filtr-soft-matte-foundation", ["oily", "combination"], "shades_foundation", "30ml", "40.00"),
    ("Makeup", "MAC", "MAC Studio Fix Fluid SPF15 Foundation", "mac-studio-fix-fluid-spf15", ["oily", "combination"], "shades_foundation", "30ml", "35.00"),
    ("Makeup", "Huda Beauty", "Huda Beauty GloWish Multidew Skin Tint", "huda-glowish-multidew-skin-tint", ["dry", "normal"], "shades_foundation", "30ml", "44.00"),
    ("Makeup", "NYX", "NYX Professional Makeup Butter Gloss Lip Gloss", "nyx-butter-gloss-lip-gloss", ["all"], "shades_lip", "8ml", "7.00"),
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


def _resolve_unique_sku(existing_skus: set[str], preferred_sku: str, slug: str, suffix: str = "") -> str:
    """Return preferred_sku if unused, otherwise a deterministic collision-free SKU."""
    if preferred_sku not in existing_skus:
        existing_skus.add(preferred_sku)
        return preferred_sku

    clean_slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    base = f"GC-{clean_slug[:65]}{'-' + suffix if suffix else ''}".upper()[:100]
    candidate = base
    counter = 1
    while candidate in existing_skus:
        tail = f"-{counter}"
        candidate = f"{base[: 100 - len(tail)]}{tail}"
        counter += 1
    existing_skus.add(candidate)
    return candidate


def _seed_blueprint_entries(
    db: Session,
    indexed_entries: list[tuple[int, tuple]],
    cat_map: dict[str, Category],
    brand_map: dict[str, Brand],
) -> int:
    """Insert missing products, variants, images, and initial batches without duplicating existing slugs."""
    today = date.today()
    created_count = 0
    existing_skus: set[str] = {s for (s,) in db.query(ProductVariant.sku).all()}
    for idx, entry in indexed_entries:
        if len(entry) == 8:
            cat_name, brand_name, prod_name, slug, skins, tpl_key, size_desc, base_price_str = entry
        else:
            cat_name, brand_name, prod_name, slug, skins, tpl_key, base_price_str = entry
            size_desc = None

        product = db.query(Product).filter(Product.slug == slug).first()
        if product is not None:
            continue
        base_price = Decimal(base_price_str)
        brand = brand_map.get(brand_name)
        if brand is None:
            brand_slug = re.sub(r"[^a-z0-9]+", "-", brand_name.lower()).strip("-")
            brand = (
                db.query(Brand)
                .filter((func.lower(Brand.slug) == brand_slug) | (func.lower(Brand.name) == brand_name.lower()))
                .first()
            )
            if brand is None:
                brand = Brand(
                    name=brand_name,
                    slug=brand_slug,
                    country_of_origin="International",
                    is_featured=True,
                    is_active=True,
                    description=f"Curated brand catalog entry for {brand_name}.",
                )
                db.add(brand)
                db.flush()
            brand_map[brand_name] = brand

        specs = {
            "origin": brand.country_of_origin or "International",
            "demo_notice": "Illustrative demo data",
        }
        if size_desc:
            specs["standard_size"] = size_desc

        product = Product(
            category_id=cat_map[cat_name].id,
            brand_id=brand.id,
            name=prod_name,
            slug=slug,
            short_description=f"Illustrative demo cosmetic entry — {prod_name}.",
            description=f"{prod_name} by {brand_name}. Demo catalog description with illustrative USD pricing for GlowCart.",
            skin_types=skins,
            specifications=specs,
            verified_ingredients=None,
            is_featured=(idx <= 15),
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
            sku = _resolve_unique_sku(
                existing_skus,
                f"GC-{idx:03d}-{v_idx:02d}",
                slug,
                suffix=f"V{v_idx:02d}",
            )
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

    # Upgrade any existing product images pointing to generic SVG or placeholders to real photographs
    updated_images = 0
    for img in db.query(ProductImage).all():
        if not img.image_url or img.image_url.endswith(".svg") or "placeholder" in img.image_url.lower() or "placehold.co" in img.image_url.lower():
            prod = db.query(Product).filter(Product.id == img.product_id).first()
            if prod and prod.category:
                img.image_url = resolve_seed_image_url(prod.category.name, prod.name, prod.slug)
                updated_images += 1

    # Ensure all products have at least one primary ProductImage
    for prod in db.query(Product).all():
        has_img = db.query(ProductImage).filter(ProductImage.product_id == prod.id).first()
        if not has_img and prod.category:
            real_url = resolve_seed_image_url(prod.category.name, prod.name, prod.slug)
            db.add(ProductImage(product_id=prod.id, image_url=real_url, is_primary=True, sort_order=0))
            updated_images += 1

    topped_up = ensure_minimum_product_count(db, target_count=100)

    if created > 0 or updated_images > 0 or topped_up > 0:
        db.commit()
        return True
    return False


# ---------------------------------------------------------------------------
# Generated 100 Products Catalog Engine
# ---------------------------------------------------------------------------
CATEGORY_CATALOG = {
    "Makeup": {
        "items": [
            "Velvet Matte Lipstick",
            "Liquid Silk Foundation",
            "Soft Pinch Liquid Blush",
            "Luminous Concealer",
            "Waterproof Volume Mascara",
            "Precision Liquid Eyeliner",
            "Dewy Setting Spray",
            "Shimmer Eyeshadow Palette",
        ],
        "images": [
            "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=600&q=80",
        ],
    },
    "Skincare": {
        "items": [
            "Barrier Restore Hydrating Serum",
            "Radiance Cleansing Balm",
            "Hyaluronic Acid Moisture Cream",
            "Niacinamide Pore Refining Toner",
            "Vitamin C Brightening Essence",
            "Overnight Peptide Repair Mask",
            "Gentle Foaming Facial Cleanser",
            "Ceramide Eye Contour Gel",
        ],
        "images": [
            "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1570194065650-d99fb4b38b15?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=600&q=80",
        ],
    },
    "Sun Care": {
        "items": [
            "Invisible Fluid Sunscreen SPF50+",
            "Tone-Up UV Defense Sun Milk",
            "Hydrating Aloe Sun Gel SPF50",
            "Matte Mineral Sun Stick",
            "Soothing After-Sun Cooling Mist",
        ],
        "images": [
            "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1526947425960-945c6e72858f?auto=format&fit=crop&w=600&q=80",
        ],
    },
    "Hair Care": {
        "items": [
            "Honey Infused Repair Hair Oil",
            "Keratin Smooth Nourishing Shampoo",
            "Argan Deep Moisture Hair Mask",
            "Heat Protectant Styling Mist",
            "Scalp Revitalizing Tonic",
        ],
        "images": [
            "https://images.unsplash.com/photo-1526947425960-945c6e72858f?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=600&q=80",
        ],
    },
    "Fragrance": {
        "items": [
            "Libre Intense Eau De Parfum",
            "Rose Velvet Eau De Toilette",
            "Vanilla Amber Hair & Body Mist",
            "White Peony Botanical Perfume",
        ],
        "images": [
            "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=600&q=80",
            "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=600&q=80",
        ],
    },
}

CATEGORIES = ["Makeup", "Skincare", "Sun Care", "Hair Care", "Fragrance"]
BRANDS = ["Atelier Lab", "GlowCart Studio", "Solis Botanica", "KeraFlora", "Velvet Veil", "Lumière Skin"]
SHADE_HEXES = ["#F3D6BE", "#E5B88E", "#C88E62", "#D98A7C", "#B85D4F", "#8E3B33", "#EADBC8"]


def generate_single_product(index: int | None = None, category: str | None = None) -> dict:
    """Generate a single cosmetic product using the category catalog items and real images."""
    category_name = (
        category
        if (category and category in CATEGORY_CATALOG)
        else random.choice(list(CATEGORY_CATALOG.keys()))
    )
    product_base_name = random.choice(CATEGORY_CATALOG[category_name]["items"])
    image_url = random.choice(CATEGORY_CATALOG[category_name]["images"])
    brand = random.choice(BRANDS)
    name = f"{product_base_name} #{index}" if index is not None else product_base_name
    price = round(random.uniform(18.0, 68.0), 2)
    stock = random.randint(20, 120)
    shade_hex = random.choice(SHADE_HEXES)
    is_popular = True if (index is not None and index <= 20) else False

    return {
        "name": name,
        "brand": brand,
        "category": category_name,
        "price": price,
        "stock": stock,
        "shade_hex": shade_hex,
        "is_popular": is_popular,
        "image_url": image_url,
    }


def generate_100_products():
    return [generate_single_product(index=i) for i in range(1, 101)]


def load_products_from_json(file_path: str | Path | None = None) -> list[dict]:
    """Load products data from a JSON file, checking given or standard candidate paths."""
    candidates: list[Path] = []
    if file_path:
        candidates.append(Path(file_path))
    candidates.extend([
        Path(__file__).parent / "products_data.json",
        Path("backend/app/db/products_data.json"),
        Path("db/products_data.json"),
        Path("../db/products_data.json"),
    ])
    for cand in candidates:
        if cand.is_file():
            with open(cand, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("Could not find products_data.json in candidate locations.")


def seed_generated_products(db: Session, products: list[dict] | None = None) -> int:
    """Seed the 100 generated products into PostgreSQL with full variants, inventory batches, and real images."""
    if products is None:
        products = generate_100_products()

    cat_map, brand_map = _ensure_categories_and_brands(db)
    today = date.today()
    created_count = 0
    existing_skus: set[str] = {s for (s,) in db.query(ProductVariant.sku).all()}

    for idx, item in enumerate(products, start=1):
        raw_slug = f"{item['brand']}-{item['name']}".lower()
        slug = re.sub(r"[^a-z0-9]+", "-", raw_slug).strip("-")

        product = db.query(Product).filter(Product.slug == slug).first()
        if product is None:
            cat = cat_map.get(item["category"]) or cat_map["Skincare"]
            brand_slug = re.sub(r"[^a-z0-9]+", "-", item["brand"].lower()).strip("-")
            brand = (
                brand_map.get(item["brand"])
                or next((b for b in brand_map.values() if b.slug == brand_slug or b.name.lower() == item["brand"].lower()), None)
            )
            if brand is None:
                brand = Brand(
                    name=item["brand"].title() if item["brand"].isupper() else item["brand"],
                    slug=brand_slug,
                    country_of_origin="International",
                    is_featured=True,
                    is_active=True,
                    description=f"Curated brand {item['brand']}",
                )
                db.add(brand)
                db.flush()
                brand_map[item["brand"]] = brand

            raw_skin = item.get("skin_type", "all").lower()
            skin_types_val = ["all"] if ("all" in raw_skin or not raw_skin) else [raw_skin]

            product = Product(
                category_id=cat.id,
                brand_id=brand.id,
                name=item["name"],
                slug=slug,
                short_description=f"Curated studio formulation — {item['name']}.",
                description=f"{item['name']} by {brand.name}. Authentic formulation with batch-verified freshness.",
                skin_types=skin_types_val,
                specifications={
                    "origin": brand.country_of_origin or "International",
                    "edition": "Studio Atelier Edition",
                },
                is_featured=item.get("is_popular", False),
                is_best_seller=item.get("is_popular", False),
                is_new_arrival=item.get("is_new_arrival", True),
                is_demo=True,
                is_active=True,
            )
            db.add(product)
            db.flush()
            created_count += 1

            # Variant with exact price, shade_name, and shade_hex
            sku = _resolve_unique_sku(
                existing_skus,
                f"GC-GEN-{idx:03d}",
                slug,
                suffix=f"G{idx:03d}",
            )
            variant = ProductVariant(
                product_id=product.id,
                sku=sku,
                price=Decimal(str(item["price"])),
                shade_name=item.get("shade_name", f"Shade #{idx}"),
                hex_color=item.get("shade_hex", "#F3D6BE"),
                status="ACTIVE",
                is_available=True,
            )
            db.add(variant)
            db.flush()

            # Primary Real Image (custom image_url or resolved unsplash)
            real_url = item.get("image_url") or resolve_seed_image_url(cat.name, item["name"], slug)
            db.add(
                ProductImage(
                    product_id=product.id,
                    image_url=real_url,
                    is_primary=True,
                    sort_order=0,
                )
            )

            # Inventory & FEFO Batch
            inv = Inventory(
                variant_id=variant.id,
                available_quantity=item["stock"],
                reserved_quantity=0,
                low_stock_threshold=10,
            )
            db.add(inv)
            db.flush()

            batch = InventoryBatch(
                variant_id=variant.id,
                batch_number=f"GEN-BATCH-{idx:03d}",
                manufacture_date=today - timedelta(days=60),
                expiry_date=today + timedelta(days=540),
                initial_quantity=item["stock"],
                remaining_quantity=item["stock"],
                received_date=today - timedelta(days=5),
            )
            db.add(batch)
            db.flush()

            db.add(
                InventoryMovement(
                    variant_id=variant.id,
                    batch_id=batch.id,
                    movement_type="RECEIVED",
                    quantity_delta=item["stock"],
                    reference_type="generated_seed",
                    reference_id=batch.batch_number,
                    reason="Initial 100 generated products stock",
                )
            )

    if created_count > 0:
        db.commit()
    return created_count


def ensure_minimum_product_count(db: Session, target_count: int = 100) -> int:
    """Top up the catalog with generated products if total product count is below target_count."""
    current_count = db.query(Product).count()
    if current_count >= target_count:
        return 0

    needed = target_count - current_count
    existing_slugs: set[str] = {s for (s,) in db.query(Product.slug).all()}
    batch: list[dict] = []
    seq = current_count + 1

    while len(batch) < needed:
        item = generate_single_product(index=seq)
        raw_slug = f"{item['brand']}-{item['name']}".lower()
        slug = re.sub(r"[^a-z0-9]+", "-", raw_slug).strip("-")
        seq += 1
        if slug in existing_slugs:
            continue
        existing_slugs.add(slug)
        batch.append(item)

    return seed_generated_products(db, batch)


if __name__ == "__main__":
    import sys
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        seed_demo_data(session)
        topped_up = ensure_minimum_product_count(session, target_count=100)
        if topped_up > 0:
            print(f"Topped up {topped_up} products to reach minimum catalog count of 100.")
        if "--json" in sys.argv:
            json_prods = load_products_from_json()
            gen_count = seed_generated_products(session, json_prods)
            print(f"Seeded {gen_count} products from products_data.json.")
        elif "--generate-100" in sys.argv or "-g" in sys.argv:
            gen_count = seed_generated_products(session)
            print(f"Generated and seeded {gen_count} additional products.")
        print("GlowCart demo data seeded successfully.")
