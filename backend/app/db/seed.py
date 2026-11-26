from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import random
import re
import zlib
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Brand,
    Cart,
    CartItem,
    Category,
    Coupon,
    Inventory,
    InventoryBatch,
    InventoryMovement,
    OrderItem,
    Product,
    ProductImage,
    ProductVariant,
    Promotion,
    Review,
    Role,
    User,
    Wishlist,
    WishlistItem,
)
from app.repositories.user_repository import UserRepository


CATEGORIES_DATA = [
    ("Makeup", "makeup", "Face, eye, and lip color cosmetics", 1),
    ("Skincare", "skincare", "Cleansers, toners, serums, essences, and moisturizers", 2),
    ("Sun Care", "sun-care", "Daily UV protection creams and sun sticks", 3),
    ("Hair Care", "hair-care", "Shampoos, conditioners, treatments, and hair masks", 4),
    ("Fragrance", "fragrance", "Perfumes, eau de parfum, and body mists", 5),
    ("Beauty Tools", "beauty-tools", "Brushes, sponges, and vanity tools", 6),
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
    ("Gisou", "gisou", "Netherlands", True),
    ("Kérastase", "kerastase", "France", True),
    ("Dyson", "dyson", "UK", True),
    ("Chanel", "chanel", "France", True),
    ("Supergoop!", "supergoop", "USA", True),
    ("Shiseido", "shiseido", "Japan", True),
    ("Biore", "biore", "Japan", False),
    ("Ouai", "ouai", "USA", False),
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
    ("Anessa", "anessa", "Japan", True),
    ("Isntree", "isntree", "South Korea", True),
    ("Tocobo", "tocobo", "South Korea", True),
    ("Rhode", "rhode", "USA", True),
    ("Drunk Elephant", "drunk-elephant", "USA", True),
    ("Tatcha", "tatcha", "Japan", True),
    ("Paula's Choice", "paulas-choice", "USA", True),
    ("Moroccanoil", "moroccanoil", "Israel", True),
    ("Amika", "amika", "USA", True),
    ("Briogeo", "briogeo", "USA", True),
    ("K18", "k18", "USA", True),
    ("Maison Francis Kurkdjian", "mfk", "France", True),
    ("Le Labo", "le-labo", "USA", True),
    ("Parfums de Marly", "parfums-de-marly", "France", True),
    ("Jo Malone", "jo-malone", "UK", True),
    ("Byredo", "byredo", "Sweden", True),
    ("Solawave", "solawave", "USA", True),
    ("Hourglass", "hourglass", "USA", True),
    ("Shu Uemura", "shu-uemura", "Japan", True),
    ("Beautyblender", "beautyblender", "USA", True),
    ("Slip", "slip", "Australia", True),
    ("Mount Lai", "mount-lai", "USA", True),
    ("Tangle Teezer", "tangle-teezer", "UK", True),
    ("Benefit Cosmetics", "benefit", "USA", True),
    ("Saie", "saie", "USA", True),
    ("SK-II", "sk-ii", "Japan", True),
    ("Summer Fridays", "summer-fridays", "USA", True),
    ("Maison Margiela", "maison-margiela", "France", True),
    ("Gucci", "gucci", "Italy", True),
    ("Calvin Klein", "calvin-klein", "USA", True),
    ("Oribe", "oribe", "USA", True),
    ("Davines", "davines", "Italy", True),
    ("Real Techniques", "real-techniques", "USA", True),
    # Additional Trending Global & Atelier Brands
    ("Abib", "abib", "South Korea", True),
    ("Ariana Grande", "ariana-grande", "USA", True),
    ("Armani Beauty", "armani-beauty", "Italy", True),
    ("Aveda", "aveda", "USA", True),
    ("Bioderma", "bioderma", "France", True),
    ("Bumble and bumble", "bumble-and-bumble", "USA", True),
    ("Burberry", "burberry", "UK", True),
    ("Canmake", "canmake", "Japan", True),
    ("Carolina Herrera", "carolina-herrera", "USA", True),
    ("Clinique", "clinique", "USA", True),
    ("Color Wow", "color-wow", "USA", True),
    ("Coola", "coola", "USA", True),
    ("Dae", "dae", "USA", True),
    ("Diptyque", "diptyque", "France", True),
    ("E.l.f.", "elf", "USA", True),
    ("EltaMD", "eltamd", "USA", True),
    ("Eucerin", "eucerin", "Germany", True),
    ("Fino", "fino", "Japan", True),
    ("Foreo", "foreo", "Sweden", True),
    ("Garnier", "garnier", "France", True),
    ("Glossier", "glossier", "USA", True),
    ("Glow Recipe", "glow-recipe", "USA", True),
    ("Haruharu Wonder", "haruharu-wonder", "South Korea", True),
    ("I'm From", "im-from", "South Korea", True),
    ("Kayali", "kayali", "UAE", True),
    ("Kiehl's", "kiehls", "USA", True),
    ("Kosas", "kosas", "USA", True),
    ("Kristin Ess", "kristin-ess", "USA", True),
    ("Laura Mercier", "laura-mercier", "USA", True),
    ("Living Proof", "living-proof", "USA", True),
    ("Makeup By Mario", "makeup-by-mario", "USA", True),
    ("Marc Jacobs", "marc-jacobs", "USA", True),
    ("Mason Pearson", "mason-pearson", "UK", True),
    ("Mielle Organics", "mielle-organics", "USA", True),
    ("NuFACE", "nuface", "USA", True),
    ("PMD", "pmd", "USA", True),
    ("Patrick Ta", "patrick-ta", "USA", True),
    ("Prada", "prada", "Italy", True),
    ("Redken", "redken", "USA", True),
    ("Revlon", "revlon", "USA", True),
    ("Sulwhasoo", "sulwhasoo", "South Korea", True),
    ("Tom Ford", "tom-ford", "USA", True),
    ("Tower 28", "tower-28", "USA", True),
    ("Tsubaki", "tsubaki", "Japan", True),
    ("Tweezerman", "tweezerman", "USA", True),
    ("Valentino", "valentino", "Italy", True),
    ("Vegamour", "vegamour", "USA", True),
    ("d'Alba", "dalba", "South Korea", True),
]

def _p(
    category: str,
    brand: str,
    name: str,
    slug: str,
    skin_types: list[str],
    variant_template: str,
    size: str,
    price: str,
    image_url: str,
) -> dict:
    digest = zlib.crc32(slug.encode("utf-8"))
    rating = round(4.7 + (digest % 3) * 0.1, 1)  # 4.7, 4.8, or 4.9
    review_count = 95 + (digest % 356)  # 95 .. 450
    return {
        "category": category,
        "brand": brand,
        "name": name,
        "slug": slug,
        "skin_types": skin_types,
        "variant_template": variant_template,
        "size": size,
        "price": price,
        "image_url": image_url,
        "rating": rating,
        "review_count": review_count,
    }


PRODUCTS_120: list[dict] = [
    # =========================================================================
    # 1. MAKEUP (20 distinct viral products)
    # =========================================================================
    _p("Makeup", "Rare Beauty", "Rare Beauty Soft Pinch Liquid Blush", "rare-beauty-soft-pinch-blush", ["all"], "shades_blush", "7.5ml", "23.00", "https://s3.amazonaws.com/donovanbailey/products/api_featured_images/000/001/003/original/open-uri20171227-4-13ivnwv?1514343870"),
    _p("Makeup", "Dior", "Dior Addict Lip Glow Oil", "dior-addict-lip-glow-oil", ["all"], "shades_lip", "6ml", "40.00", "/images/products/luxury-lip-hand.jpg"),
    _p("Makeup", "Charlotte Tilbury", "Charlotte Tilbury Airbrush Flawless Setting Spray", "ct-airbrush-flawless-setting-spray", ["all"], "volumes", "100ml", "38.00", "https://images.unsplash.com/photo-1688955665338-fb430ff8436d?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "Fenty Beauty", "Fenty Beauty Gloss Bomb Universal Lip Luminizer", "fenty-gloss-bomb-luminizer", ["all"], "shades_lip", "9ml", "21.00", "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "NARS", "NARS Radiant Creamy Concealer", "nars-radiant-creamy-concealer", ["all"], "shades_foundation", "6ml", "32.00", "https://images.unsplash.com/photo-1571875257727-256c39da42af?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "MAC", "MAC Matte Lipstick Velvet Teddy", "mac-matte-lipstick-velvet-teddy", ["all"], "shades_lip", "3g", "23.00", "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "Yves Saint Laurent", "YSL Lash Clash Extreme Volume Mascara", "ysl-lash-clash-mascara", ["all"], "shades_eye", "9ml", "32.00", "https://images.unsplash.com/photo-1631214540553-ff044a3ff1d4?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "Huda Beauty", "Huda Beauty Easy Bake Loose Baking & Setting Powder", "huda-easy-bake-loose-powder", ["oily", "combination"], "shades_powder", "20g", "38.00", "https://cdn.dummyjson.com/product-images/beauty/powder-canister/thumbnail.webp"),
    _p("Makeup", "Rhode", "Rhode Peptide Lip Tint", "rhode-peptide-lip-tint", ["all"], "shades_lip", "10ml", "18.00", "https://images.unsplash.com/photo-1571875227232-b7bd1fe2ed80?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "Summer Fridays", "Summer Fridays Lip Butter Balm", "summer-fridays-lip-butter-balm", ["all", "dry"], "shades_lip", "15g", "24.00", "/images/products/unbranded-lipstick.jpg"),
    _p("Makeup", "Saie", "Saie Glowy Super Gel Lightweight Dewy Highlighter", "saie-glowy-super-gel", ["all", "dry"], "shades_blush", "30ml", "28.00", "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "Kosas", "Kosas Revealer Concealer", "kosas-revealer-concealer", ["dry", "all"], "shades_foundation", "6ml", "30.00", "/images/products/unbranded-foundation-square.jpg"),
    _p("Makeup", "Benefit Cosmetics", "Benefit 24-HR Brow Setter Clear Gel", "benefit-24hr-brow-setter", ["all"], "volumes", "7ml", "26.00", "https://s3.amazonaws.com/donovanbailey/products/api_featured_images/000/001/040/original/open-uri20180630-4-1afkyee?1530390386"),
    _p("Makeup", "Patrick Ta", "Patrick Ta Major Headlines Blush", "patrick-ta-major-headlines-blush", ["all"], "shades_blush", "6g", "38.00", "/images/products/art-blush-compact.jpg"),
    _p("Makeup", "Armani Beauty", "Armani Luminous Silk Foundation", "armani-luminous-silk-foundation", ["all", "combination"], "shades_foundation", "30ml", "69.00", "/images/products/art-foundation-beige.jpg"),
    _p("Makeup", "Makeup By Mario", "Makeup By Mario SoftSculpt Skin Enhancer", "makeup-by-mario-skin-enhancer", ["all"], "shades_powder", "5g", "32.00", "/images/products/compact-cushion-hand.jpg"),
    _p("Makeup", "Tower 28", "Tower 28 MakeWaves Mascara", "tower-28-makewaves-mascara", ["sensitive", "all"], "shades_eye", "8.5ml", "20.00", "/images/products/art-mascara-tube.jpg"),
    _p("Makeup", "Clinique", "Clinique Almost Lipstick Black Honey", "clinique-almost-lipstick-black-honey", ["all"], "shades_lip", "1.9g", "24.00", "/images/products/art-nude-lipstick.jpg"),
    _p("Makeup", "Laura Mercier", "Laura Mercier Translucent Loose Setting Powder", "laura-mercier-translucent-powder", ["all", "oily"], "shades_powder", "29g", "43.00", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80"),
    _p("Makeup", "Rom&nd", "Rom&nd Juicy Lasting Tint", "romand-juicy-lasting-tint", ["all"], "shades_lip", "5.5g", "11.50", "https://images.unsplash.com/photo-1583209814683-c023dd293cc6?auto=format&fit=crop&w=800&q=80"),

    # =========================================================================
    # 2. SKINCARE (20 distinct viral products)
    # =========================================================================
    _p("Skincare", "COSRX", "COSRX Advanced Snail 96 Mucin Power Essence", "cosrx-advanced-snail-96-essence", ["dry", "sensitive"], "volumes", "100ml", "21.00", "https://images.unsplash.com/photo-1777450793530-99a0e7b7fc53?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Anua", "Anua Heartleaf 77% Soothing Toner", "anua-heartleaf-77-soothing-toner", ["sensitive", "oily"], "volumes", "250ml", "23.00", "/images/products/unbranded-toner.jpg"),
    _p("Skincare", "Torriden", "Torriden DIVE-IN Hyaluronic Acid Serum", "torriden-dive-in-ha-serum", ["dry", "dehydrated", "all"], "volumes", "50ml", "20.00", "/images/products/serum-dropper-hand.jpg"),
    _p("Skincare", "SKIN1004", "SKIN1004 Madagascar Centella Ampoule", "skin1004-madagascar-centella-ampoule", ["sensitive", "all"], "volumes", "55ml", "18.50", "https://images.unsplash.com/photo-1788700632990-d337396576a1?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Laneige", "Laneige Lip Sleeping Mask", "laneige-lip-sleeping-mask", ["all", "dry"], "sizes", "20g", "24.00", "https://plus.unsplash.com/premium_photo-1674739375749-7efe56fc8bbb?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Medicube", "Medicube Collagen Night Wrapping Mask", "medicube-collagen-night-mask", ["dry", "all"], "volumes", "75ml", "28.00", "/images/products/unbranded-cream-jar.jpg"),
    _p("Skincare", "Rhode", "Rhode Glazing Milk Ceramide Facial Essence", "rhode-glazing-milk", ["dry", "sensitive", "all"], "volumes", "140ml", "30.00", "https://images.unsplash.com/photo-1771329064159-33f758d91f4a?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Tatcha", "Tatcha The Dewy Skin Cream", "tatcha-dewy-skin-cream", ["dry", "normal"], "volumes", "50ml", "72.00", "https://images.unsplash.com/photo-1608068811588-3a67006b7489?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Paula's Choice", "Paula's Choice 2% BHA Liquid Exfoliant", "paulas-choice-2-bha-exfoliant", ["oily", "combination"], "volumes", "118ml", "35.00", "https://images.unsplash.com/photo-1764585966150-13611b2fee39?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Estée Lauder", "Estée Lauder Advanced Night Repair Serum", "estee-lauder-advanced-night-repair", ["dry", "mature", "all"], "volumes", "50ml", "85.00", "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "The Ordinary", "The Ordinary Niacinamide 10% + Zinc 1%", "the-ordinary-niacinamide-10-zinc-1", ["oily", "combination"], "volumes", "30ml", "6.50", "https://images.unsplash.com/photo-1767256046031-743d33937c4e?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "CeraVe", "CeraVe Hydrating Facial Cleanser", "cerave-hydrating-facial-cleanser", ["dry", "sensitive"], "volumes", "236ml", "15.99", "https://images.unsplash.com/photo-1749599018738-b8fb6c4a83e0?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "La Roche-Posay", "La Roche-Posay Cicaplast Baume B5", "lrp-cicaplast-baume-b5", ["sensitive", "dry"], "volumes", "100ml", "18.99", "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "SK-II", "SK-II Facial Treatment Essence", "sk-ii-facial-treatment-essence", ["all", "mature"], "volumes", "160ml", "185.00", "https://images.unsplash.com/photo-1770732766528-d0e9fd0df233?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Drunk Elephant", "Drunk Elephant Protini Polypeptide Cream", "drunk-elephant-protini-cream", ["all", "mature"], "volumes", "50ml", "68.00", "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Glow Recipe", "Glow Recipe Watermelon Glow Niacinamide Dew Drops", "glow-recipe-dew-drops", ["all", "dull"], "volumes", "40ml", "35.00", "https://images.unsplash.com/photo-1741896135490-4062a3b21abf?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Bioderma", "Bioderma Sensibio H2O Micellar Water", "bioderma-sensibio-h2o", ["sensitive", "all"], "volumes", "500ml", "18.99", "https://images.unsplash.com/photo-1531895861208-8504b98fe814?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Sulwhasoo", "Sulwhasoo First Care Activating Serum", "sulwhasoo-first-care-serum", ["all", "mature"], "volumes", "60ml", "89.00", "https://images.unsplash.com/photo-1782086816100-017c99c45109?auto=format&fit=crop&w=800&q=80"),
    _p("Skincare", "Kiehl's", "Kiehl's Ultra Facial Cream", "kiehls-ultra-facial-cream", ["dry", "all"], "volumes", "50ml", "38.00", "/images/products/art-moisturizer-jar.jpg"),
    _p("Skincare", "I'm From", "I'm From Rice Toner", "im-from-rice-toner", ["dry", "dull"], "volumes", "150ml", "28.00", "/images/products/art-minimalist-toner.jpg"),

    # =========================================================================
    # 3. SUN CARE (20 distinct viral products)
    # =========================================================================
    _p("Sun Care", "Beauty of Joseon", "Beauty of Joseon Relief Sun Rice + Probiotics SPF50+", "boj-relief-sun", ["all", "sensitive"], "volumes", "50ml", "18.00", "/images/products/unbranded-sunscreen.jpg"),
    _p("Sun Care", "Round Lab", "Round Lab Birch Juice Moisturizing Sun Cream", "round-lab-birch-sun", ["dry", "normal"], "volumes", "50ml", "21.00", "https://plus.unsplash.com/premium_photo-1682535210542-21dceae4530c?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "SKIN1004", "SKIN1004 Hyalu-Cica Water-Fit Sun Serum SPF50+", "skin1004-sun-serum", ["dry", "all"], "volumes", "50ml", "16.50", "https://images.unsplash.com/photo-1643379855997-5344bd8d3e78?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Anessa", "Anessa Perfect UV Sunscreen Skincare Milk SPF50+", "anessa-perfect-uv-milk", ["oily", "combination"], "volumes", "60ml", "34.00", "https://plus.unsplash.com/premium_photo-1664300261771-f53155289841?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Supergoop!", "Supergoop! Unseen Sunscreen SPF 40", "supergoop-unseen-sunscreen-spf40", ["all"], "volumes", "50ml", "38.00", "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Supergoop!", "Supergoop! Glowscreen SPF 40", "supergoop-glowscreen-spf40", ["all", "dry"], "volumes", "50ml", "38.00", "https://images.unsplash.com/photo-1784256543053-076f2a8e4e40?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "La Roche-Posay", "La Roche-Posay Anthelios UVMune 400 Fluid", "lrp-anthelios-fluid", ["sensitive", "all"], "volumes", "50ml", "33.50", "https://plus.unsplash.com/premium_photo-1663100784433-ac60688b5fe3?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Isntree", "Isntree Hyaluronic Acid Watery Sun Gel SPF50+", "isntree-watery-sun-gel", ["dry", "all"], "volumes", "50ml", "19.00", "https://plus.unsplash.com/premium_photo-1679046948909-ab47e96082e7?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Tocobo", "Tocobo Cotton Soft Sun Stick SPF50+", "tocobo-cotton-soft-sun-stick", ["oily", "combination"], "sizes", "19g", "17.00", "https://plus.unsplash.com/premium_photo-1673628167571-532a6c5f5d16?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Biore", "Biore UV Aqua Rich Watery Essence", "biore-uv-aqua-rich-essence", ["all", "oily"], "volumes", "50g", "15.00", "https://images.unsplash.com/photo-1786298300597-1e05c974aafa?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Shiseido", "Shiseido Clear Sunscreen Stick SPF 50+", "shiseido-clear-sunscreen-stick", ["all"], "sizes", "20g", "30.00", "https://images.unsplash.com/photo-1576426863848-c21f53c60b19?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "EltaMD", "EltaMD UV Clear Broad-Spectrum SPF 46", "eltamd-uv-clear-spf46", ["acne-prone", "sensitive"], "volumes", "48g", "41.00", "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Haruharu Wonder", "Haruharu Wonder Black Rice Moisture Airyfit Sunscreen", "haruharu-black-rice-sunscreen", ["all"], "volumes", "50ml", "18.00", "/images/products/art-sunscreen-tube.jpg"),
    _p("Sun Care", "Canmake", "Canmake Mermaid Skin Gel UV", "canmake-mermaid-skin-gel", ["dry", "all"], "volumes", "40g", "12.00", "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Abib", "Abib Quick Sunstick Protection Bar", "abib-quick-sunstick-bar", ["all"], "sizes", "22g", "20.00", "https://images.unsplash.com/photo-1680063122329-69ef93b72c53?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Eucerin", "Eucerin Oil Control Sun Gel-Cream", "eucerin-oil-control-sun-gel", ["oily", "acne-prone"], "volumes", "50ml", "22.00", "https://images.unsplash.com/photo-1515377905703-c4788e51af15?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Coola", "Coola Classic Face Sunscreen", "coola-classic-face-sunscreen", ["all"], "volumes", "50ml", "32.00", "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "Innisfree", "Innisfree Daily UV Defense Sunscreen", "innisfree-daily-uv-defense", ["dry", "normal"], "volumes", "50ml", "16.00", "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "COSRX", "Cosrx Aloe Soothing Sun Cream", "cosrx-aloe-soothing-sun-cream", ["dry", "sensitive"], "volumes", "50ml", "16.00", "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80"),
    _p("Sun Care", "d'Alba", "d'Alba Waterfull Essence Sun Cream", "dalba-waterfull-sun-cream", ["all", "dry"], "volumes", "50ml", "26.00", "https://images.unsplash.com/photo-1526947425960-945c6e72858f?auto=format&fit=crop&w=800&q=80"),

    # =========================================================================
    # 4. HAIR CARE (20 distinct viral products)
    # =========================================================================
    _p("Hair Care", "Gisou", "Gisou Honey Infused Hair Oil", "gisou-honey-infused-hair-oil", ["all", "dry"], "volumes", "50ml", "46.00", "https://images.unsplash.com/photo-1669281393011-c335050cf0e9?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "K18", "K18 Leave-In Molecular Repair Hair Mask", "k18-leave-in-molecular-mask", ["all", "damaged"], "volumes", "50ml", "75.00", "https://images.unsplash.com/photo-1643123158251-3a66f53a4635?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Olaplex", "Olaplex No. 3 Hair Perfector", "olaplex-no-3-hair-perfector", ["all", "damaged"], "volumes", "100ml", "30.00", "https://plus.unsplash.com/premium_photo-1692825694870-10196b7640f9?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Olaplex", "Olaplex No. 7 Bonding Oil", "olaplex-no-7-bonding-oil", ["all"], "volumes", "30ml", "30.00", "https://images.unsplash.com/photo-1643123158489-634259c983b3?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Ouai", "Ouai Leave-In Conditioner", "ouai-leave-in-conditioner", ["all", "dry"], "volumes", "140ml", "30.00", "https://images.unsplash.com/photo-1620916297397-a4a5402a3c6c?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Amika", "Amika Soulfood Nourishing Mask", "amika-soulfood-mask", ["dry", "all"], "volumes", "250ml", "34.00", "https://images.unsplash.com/photo-1758544518111-53274094598e?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Briogeo", "Briogeo Don't Despair Repair Mask", "briogeo-dont-despair-repair-mask", ["dry", "damaged"], "volumes", "237ml", "39.00", "https://plus.unsplash.com/premium_photo-1661898281541-b0b724b6257b?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Color Wow", "Color Wow Dream Coat Supernatural Spray", "color-wow-dream-coat-spray", ["all"], "volumes", "200ml", "28.00", "https://images.unsplash.com/photo-1661347243240-5ce7c9992369?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Mielle Organics", "Mielle Rosemary Mint Scalp & Hair Strengthening Oil", "mielle-rosemary-mint-oil", ["all"], "volumes", "59ml", "10.00", "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Fino", "Fino Premium Touch Hair Mask", "fino-premium-touch-hair-mask", ["damaged", "dry"], "sizes", "230g", "15.00", "https://plus.unsplash.com/premium_photo-1700162640179-cd0c0005320c?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Tsubaki", "Tsubaki Premium Repair Mask", "tsubaki-premium-repair-mask", ["damaged", "dry"], "sizes", "180g", "16.00", "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Dae", "Dae Cactus Fruit 3-in-1 Styling Cream", "dae-cactus-fruit-styling-cream", ["all"], "volumes", "150ml", "30.00", "https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Vegamour", "Vegamour GRO Hair Serum", "vegamour-gro-hair-serum", ["thinning", "all"], "volumes", "30ml", "64.00", "https://images.unsplash.com/photo-1771955216611-0a826d819978?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Kristin Ess", "Kristin Ess Signature Shampoo", "kristin-ess-signature-shampoo", ["all"], "volumes", "296ml", "15.00", "https://cdn.dummyjson.com/product-images/skin-care/attitude-super-leaves-hand-soap/thumbnail.webp"),
    _p("Hair Care", "Living Proof", "Living Proof Perfect Hair Day Dry Shampoo", "living-proof-dry-shampoo", ["all"], "volumes", "198ml", "30.00", "https://plus.unsplash.com/premium_photo-1661630984481-e29093921ff7?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Oribe", "Oribe Gold Lust Repair & Restore Shampoo", "oribe-gold-lust-shampoo", ["all", "damaged"], "volumes", "250ml", "49.00", "https://cdn.dummyjson.com/product-images/skin-care/olay-ultra-moisture-shea-butter-body-wash/thumbnail.webp"),
    _p("Hair Care", "Aveda", "Aveda Botanical Repair Strengthening Leave-In", "aveda-botanical-repair-leave-in", ["all", "damaged"], "volumes", "100ml", "38.00", "https://cdn.dummyjson.com/product-images/skin-care/vaseline-men-body-and-face-lotion/thumbnail.webp"),
    _p("Hair Care", "Bumble and bumble", "Bumble and bumble Hairdresser's Invisible Oil", "bumble-hairdressers-invisible-oil", ["all", "dry"], "volumes", "100ml", "45.00", "https://images.unsplash.com/photo-1765726951362-df46f5a74cdf?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Redken", "Redken Acidic Bonding Concentrate", "redken-acidic-bonding-concentrate", ["damaged", "all"], "volumes", "150ml", "32.00", "https://plus.unsplash.com/premium_photo-1679046947964-139a2256afb5?auto=format&fit=crop&w=800&q=80"),
    _p("Hair Care", "Garnier", "Garnier Fructis Hair Food Banana Mask", "garnier-hair-food-banana-mask", ["dry", "all"], "volumes", "390ml", "9.00", "https://images.unsplash.com/photo-1568584711271-6c929fb49b60?auto=format&fit=crop&w=800&q=80"),

    # =========================================================================
    # 5. FRAGRANCE (20 distinct viral products)
    # =========================================================================
    _p("Fragrance", "Maison Francis Kurkdjian", "Maison Francis Kurkdjian Baccarat Rouge 540", "mfk-baccarat-rouge-540", ["all"], "volumes", "70ml", "325.00", "https://images.unsplash.com/photo-1632928145408-ef47a7672964?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Le Labo", "Le Labo Santal 33 Eau de Parfum", "le-labo-santal-33", ["all"], "volumes", "50ml", "230.00", "https://images.unsplash.com/photo-1609175235148-2fe181db7f36?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Yves Saint Laurent", "Yves Saint Laurent Libre Eau de Parfum", "ysl-libre-eau-de-parfum", ["all"], "volumes", "50ml", "98.00", "https://cdn.dummyjson.com/product-images/fragrances/chanel-coco-noir-eau-de/thumbnail.webp"),
    _p("Fragrance", "Parfums de Marly", "Parfums de Marly Delina", "pdm-delina-eau-de-parfum", ["all"], "volumes", "75ml", "355.00", "https://cdn.dummyjson.com/product-images/fragrances/gucci-bloom-eau-de/thumbnail.webp"),
    _p("Fragrance", "Sol de Janeiro", "Sol de Janeiro Cheirosa 62 Perfume Mist", "sdj-cheirosa-62-mist", ["all"], "volumes", "90ml", "24.00", "https://images.unsplash.com/photo-1784902538196-c7d914e3ecce?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Dior", "Dior Miss Dior Blooming Bouquet", "miss-dior-blooming-bouquet", ["all"], "volumes", "50ml", "95.00", "https://cdn.dummyjson.com/product-images/fragrances/dior-j'adore/thumbnail.webp"),
    _p("Fragrance", "Jo Malone", "Jo Malone Wood Sage & Sea Salt", "jo-malone-wood-sage-sea-salt", ["all"], "volumes", "100ml", "165.00", "https://images.unsplash.com/photo-1666621630026-862eea07236c?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Byredo", "Byredo Mojave Ghost", "byredo-mojave-ghost", ["all"], "volumes", "100ml", "290.00", "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Maison Margiela", "Maison Margiela Replica By the Fireplace", "maison-margiela-replica-fireplace", ["all"], "volumes", "100ml", "165.00", "https://cdn.dummyjson.com/product-images/fragrances/calvin-klein-ck-one/thumbnail.webp"),
    _p("Fragrance", "Chanel", "Chanel Coco Mademoiselle", "chanel-coco-mademoiselle", ["all"], "volumes", "100ml", "172.00", "https://cdn.dummyjson.com/product-images/fragrances/dolce-shine-eau-de/thumbnail.webp"),
    _p("Fragrance", "Tom Ford", "Tom Ford Lost Cherry", "tom-ford-lost-cherry", ["all"], "volumes", "50ml", "395.00", "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Kayali", "Kayali Vanilla 28", "kayali-vanilla-28", ["all"], "volumes", "50ml", "89.00", "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Ariana Grande", "Ariana Grande Cloud Eau de Parfum", "ariana-grande-cloud-edp", ["all"], "volumes", "100ml", "65.00", "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Glossier", "Glossier You Eau de Parfum", "glossier-you-edp", ["all"], "volumes", "50ml", "68.00", "https://images.unsplash.com/photo-1523293182086-7651a899d37f?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Burberry", "Burberry Goddess Eau de Parfum", "burberry-goddess-edp", ["all"], "volumes", "50ml", "110.00", "https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Valentino", "Valentino Donna Born In Roma", "valentino-donna-born-in-roma", ["all"], "volumes", "50ml", "135.00", "https://images.unsplash.com/photo-1615397349754-cfa2066a298e?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Prada", "Prada Paradoxe Eau de Parfum", "prada-paradoxe-edp", ["all"], "volumes", "50ml", "135.00", "https://images.unsplash.com/photo-1616949755610-8c9bbc08f138?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Diptyque", "Diptyque Philosykos Eau de Toilette", "diptyque-philosykos-edt", ["all"], "volumes", "100ml", "175.00", "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Carolina Herrera", "Carolina Herrera Good Girl", "carolina-herrera-good-girl", ["all"], "volumes", "80ml", "140.00", "https://images.unsplash.com/photo-1528720208104-3d9bd03cc9d4?auto=format&fit=crop&w=800&q=80"),
    _p("Fragrance", "Marc Jacobs", "Marc Jacobs Daisy Eau So Fresh", "marc-jacobs-daisy-eau-so-fresh", ["all"], "volumes", "75ml", "118.00", "https://images.unsplash.com/photo-1587017539504-67cfbddac569?auto=format&fit=crop&w=800&q=80"),

    # =========================================================================
    # 6. BEAUTY TOOLS (20 distinct viral tools & styling devices)
    # =========================================================================
    _p("Beauty Tools", "Dyson", "Dyson Airwrap Multi-Styler", "dyson-airwrap-multi-styler", ["all"], "sizes", "Set", "599.00", "https://images.unsplash.com/photo-1712641966810-611ff1503c6d?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Dyson", "Dyson Supersonic Hair Dryer", "dyson-supersonic-hair-dryer", ["all"], "sizes", "Device", "429.00", "https://images.unsplash.com/photo-1727364438136-6edc10ef0a52?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Medicube", "Medicube Age-R Booster Pro", "medicube-age-r-booster-pro", ["all", "mature"], "sizes", "Device", "280.00", "https://plus.unsplash.com/premium_photo-1734469071552-3ac334be70f7?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Hourglass", "Hourglass Vanish Seamless Finish Foundation Brush", "hourglass-vanish-foundation-brush", ["all"], "sizes", "1 pc", "48.00", "https://images.unsplash.com/photo-1553380155-da0ccd2e55e0?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Rare Beauty", "Rare Beauty Liquid Blush Brush", "rare-beauty-liquid-blush-brush", ["all"], "sizes", "1 pc", "18.00", "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Real Techniques", "Real Techniques Everyday Essentials Brush Set", "real-techniques-brush-set", ["all"], "sizes", "5-pc Set", "22.00", "https://images.unsplash.com/photo-1748899440472-d044c12e8316?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Beautyblender", "Beautyblender Original Makeup Sponge", "beautyblender-original-sponge", ["all"], "sizes", "1 pc", "20.00", "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Shu Uemura", "Shu Uemura Eyelash Curler", "shu-uemura-eyelash-curler", ["all"], "sizes", "1 pc", "25.00", "/images/products/unbranded-mascara.jpg"),
    _p("Beauty Tools", "Mount Lai", "Mount Lai Jade Gua Sha", "mount-lai-jade-gua-sha", ["all"], "sizes", "1 pc", "34.00", "https://plus.unsplash.com/premium_photo-1661583880955-7b21fe8f7f00?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Slip", "Slip Pure Silk Pillowcase", "slip-pure-silk-pillowcase", ["all", "sensitive"], "sizes", "Queen", "89.00", "https://plus.unsplash.com/premium_photo-1664543258940-69c4480c5e8f?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Tangle Teezer", "Tangle Teezer Ultimate Detangler", "tangle-teezer-ultimate-detangler", ["all"], "sizes", "1 pc", "16.00", "https://images.unsplash.com/photo-1713180758582-9bac6bc62a26?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "NuFACE", "NuFACE Trinity+ Facial Toning Device", "nuface-trinity-facial-toning", ["all", "mature"], "sizes", "Device", "395.00", "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Foreo", "Foreo Luna 4 Facial Cleansing Brush", "foreo-luna-4-cleansing-brush", ["all"], "sizes", "Device", "219.00", "https://images.unsplash.com/photo-1512437136892-3d200c4645b9?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Revlon", "Revlon One-Step Volumizer", "revlon-one-step-volumizer", ["all"], "sizes", "Styling Tool", "59.99", "https://plus.unsplash.com/premium_photo-1674949802338-f94005eb5b0a?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Tweezerman", "Tweezerman Slant Tweezer", "tweezerman-slant-tweezer", ["all"], "sizes", "1 pc", "24.00", "https://s3.amazonaws.com/donovanbailey/products/api_featured_images/000/000/985/original/data?1514082775"),
    _p("Beauty Tools", "Fenty Beauty", "Fenty Beauty Precision Makeup Sponge", "fenty-precision-makeup-sponge", ["all"], "sizes", "1 pc", "16.00", "https://plus.unsplash.com/premium_photo-1684407616442-8d5a1b7c978e?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Charlotte Tilbury", "Charlotte Tilbury Hollywood Complexion Brush", "ct-hollywood-complexion-brush", ["all"], "sizes", "1 pc", "45.00", "https://images.unsplash.com/photo-1538022890810-8f4000ca9a10?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "E.l.f.", "E.l.f. Putty Primer Applicator", "elf-putty-primer-applicator", ["all"], "sizes", "1 pc", "6.00", "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "Mason Pearson", "Mason Pearson Handy Bristle Hair Brush", "mason-pearson-handy-bristle-brush", ["all"], "sizes", "1 pc", "175.00", "https://images.unsplash.com/photo-1522337660859-02fbefca4702?auto=format&fit=crop&w=800&q=80"),
    _p("Beauty Tools", "PMD", "PMD Clean Smart Facial Cleansing Device", "pmd-clean-smart-device", ["all"], "sizes", "Device", "99.00", "https://images.unsplash.com/photo-1512207576147-99bc3066b621?auto=format&fit=crop&w=800&q=80"),
]

assert len(PRODUCTS_120) == 120, f"Expected 120 products, got {len(PRODUCTS_120)}"
assert len({p["image_url"] for p in PRODUCTS_120}) == 120, "Duplicate image_url in PRODUCTS_120!"
assert len({p["slug"] for p in PRODUCTS_120}) == 120, "Duplicate slug in PRODUCTS_120!"
assert len({p["name"] for p in PRODUCTS_120}) == 120, "Duplicate name in PRODUCTS_120!"

# Backwards compatibility alias
PRODUCTS_100: list[dict] = PRODUCTS_120

SLUG_IMAGE_MAP: dict[str, str] = {p["slug"]: p["image_url"] for p in PRODUCTS_120}

CATALOG_BLUEPRINT = [
    (
        p["category"],
        p["brand"],
        p["name"],
        p["slug"],
        p["skin_types"],
        p["variant_template"],
        p["size"],
        p["price"],
    )
    for p in PRODUCTS_100
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


VERIFIED_COSMETIC_IMAGE_URLS = [
    "/images/products/fenty-foundation-hand.jpg",
    "/images/products/unbranded-foundation-square.jpg",
    "/images/products/luxury-lip-hand.jpg",
    "/images/products/compact-cushion-hand.jpg",
    "/images/products/serum-dropper-hand.jpg",
    "/images/products/unbranded-lipstick.jpg",
    "/images/products/unbranded-blush.jpg",
    "/images/products/unbranded-mascara.jpg",
    "/images/products/unbranded-sunscreen.jpg",
    "/images/products/unbranded-cream-jar.jpg",
    "/images/products/unbranded-toner.jpg",
    "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1596704017254-9b121068fb31?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=800&q=80",
]

BROKEN_IMAGE_URLS = {
    "https://images.unsplash.com/photo-1556228722-d0b5eb1c11d5?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1567928815116-3e33b006c6e7?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1570194065650-d99fb4b38b15?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1570194065650-d99fb4b38b15?auto=format&fit=crop&w=600&q=80",
    # Portrait-only / hair-touching lifestyle photos (no cosmetic product in frame)
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=800&q=80",
    # Competing brand logos (Clinique, Chanel, Curology, Maui Moisture, Cocooil)
    "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1526947425960-945c6e72858f?auto=format&fit=crop&w=800&q=80",
}

SLUG_SHOWCASE_IMAGES: dict[str, str] = {
    "fenty-pro-filtr-soft-matte-foundation": "/images/products/fenty-foundation-hand.jpg",
    "fenty-gloss-bomb-luminizer": "/images/products/luxury-lip-hand.jpg",
    "laneige-neo-cushion-matte": "/images/products/compact-cushion-hand.jpg",
    "torriden-dive-in-ha-serum": "/images/products/serum-dropper-hand.jpg",
}

PRODUCT_TYPE_IMAGE_POOLS: dict[str, list[str]] = {
    "foundation_concealer": [
        "/images/products/fenty-foundation-hand.jpg",
        "/images/products/unbranded-foundation-square.jpg",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "/images/products/compact-cushion-hand.jpg",
    ],
    "blush_powder": [
        "/images/products/unbranded-blush.jpg",
        "/images/products/compact-cushion-hand.jpg",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80",
    ],
    "lipstick_gloss": [
        "/images/products/luxury-lip-hand.jpg",
        "/images/products/unbranded-lipstick.jpg",
        "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80",
    ],
    "eye_makeup": [
        "https://images.unsplash.com/photo-1596704017254-9b121068fb31?auto=format&fit=crop&w=800&q=80",
        "/images/products/unbranded-mascara.jpg",
        "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
    ],
    "serum_ampoule": [
        "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
        "/images/products/serum-dropper-hand.jpg",
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
    ],
    "toner_essence": [
        "/images/products/unbranded-toner.jpg",
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
    ],
    "cleanser": [
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "/images/products/unbranded-toner.jpg",
    ],
    "moisturizer_cream": [
        "/images/products/unbranded-cream-jar.jpg",
        "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
    ],
    "sunscreen": [
        "/images/products/unbranded-sunscreen.jpg",
        "/images/products/unbranded-toner.jpg",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "/images/products/unbranded-cream-jar.jpg",
    ],
    "hair_care": [
        "/images/products/serum-dropper-hand.jpg",
        "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80",
        "/images/products/unbranded-cream-jar.jpg",
        "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
    ],
    "perfume": [
        "https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=800&q=80",
    ],
    "body_tools": [
        "https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1596704017254-9b121068fb31?auto=format&fit=crop&w=800&q=80",
    ],
}

# Strict product-type keyword -> exact matching clean/unbranded photos
ITEM_TYPE_IMAGE_RULES: list[tuple[tuple[str, ...], list[str]]] = [
    (("foundation", "skin tint", "concealer"), PRODUCT_TYPE_IMAGE_POOLS["foundation_concealer"]),
    (("cushion", "powder", "blush"), PRODUCT_TYPE_IMAGE_POOLS["blush_powder"]),
    (("lip oil", "lip gloss", "gloss", "luminizer", "lip sleeping mask", "lip mask", "lip balm", "matte ink", "lipstick", "lip crayon", "lip tint"), PRODUCT_TYPE_IMAGE_POOLS["lipstick_gloss"]),
    (("mascara", "eyeliner", "eyeshadow", "palette"), PRODUCT_TYPE_IMAGE_POOLS["eye_makeup"]),
    (("setting spray", "toner", "essence", "pad", "solution"), PRODUCT_TYPE_IMAGE_POOLS["toner_essence"]),
    (("sun", "spf", "uv"), PRODUCT_TYPE_IMAGE_POOLS["sunscreen"]),
    (("serum", "ampoule", "ampule", "drop"), PRODUCT_TYPE_IMAGE_POOLS["serum_ampoule"]),
    (("cleanser", "wash"), PRODUCT_TYPE_IMAGE_POOLS["cleanser"]),
    (("cream", "lotion", "balm", "butter", "mask", "pudding", "thanakha"), PRODUCT_TYPE_IMAGE_POOLS["moisturizer_cream"]),
    (("dyson", "airwrap", "styler"), ["https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=800&q=80"]),
    (("shampoo", "conditioner", "hair", "olaplex", "gisou", "kérastase", "kerastase", "ouai"), PRODUCT_TYPE_IMAGE_POOLS["hair_care"]),
    (("perfume", "parfum", "toilette", "mist", "fragrance"), PRODUCT_TYPE_IMAGE_POOLS["perfume"]),
    (("brush", "sponge", "set", "kit", "bundle"), PRODUCT_TYPE_IMAGE_POOLS["body_tools"]),
]


def _build_category_pool(priority_indices: list[int]) -> list[str]:
    """Build an ordered unique URL pool starting with category-specific indices."""
    ordered = [VERIFIED_COSMETIC_IMAGE_URLS[i] for i in priority_indices if i < len(VERIFIED_COSMETIC_IMAGE_URLS)]
    for url in VERIFIED_COSMETIC_IMAGE_URLS:
        if url not in ordered:
            ordered.append(url)
    return ordered


CATEGORY_IMAGE_POOLS: dict[str, list[str]] = {
    "Makeup": _build_category_pool([0, 1, 2, 3, 5, 6, 7, 11, 12, 13, 14, 15, 16]),
    "Skincare": _build_category_pool([4, 9, 10, 14, 17, 18, 19, 8]),
    "Sun Care": _build_category_pool([8, 9, 10, 14, 17, 18, 19]),
    "Hair Care": _build_category_pool([19, 20, 10, 14, 17]),
    "Body Care": _build_category_pool([9, 17, 18, 19, 14, 10]),
    "Fragrance": _build_category_pool([21, 2, 5, 6, 11, 12]),
    "Beauty Tools": _build_category_pool([11, 15, 16, 3, 6, 7]),
    "Makeup Sets": _build_category_pool([11, 12, 15, 16, 0, 1, 2, 3, 5, 6]),
}


def _resolve_item_type_pool(cat_name: str, prod_name: str, slug: str) -> list[str]:
    """Return the strict list of matching images for a product's item type."""
    if slug in SLUG_IMAGE_MAP:
        return [SLUG_IMAGE_MAP[slug]]
    if slug in SLUG_SHOWCASE_IMAGES:
        return [SLUG_SHOWCASE_IMAGES[slug]]
    lower_name = prod_name.lower()
    for keywords, urls in ITEM_TYPE_IMAGE_RULES:
        if any(kw in lower_name for kw in keywords):
            return urls
    return CATEGORY_IMAGE_POOLS.get(cat_name, VERIFIED_COSMETIC_IMAGE_URLS)


def resolve_seed_image_url(
    cat_name: str,
    prod_name: str,
    slug: str,
    index: int | None = None,
) -> str:
    """Return the dedicated 1-to-1 hardcoded Unsplash URL for PRODUCTS_100, or type-matched fallback."""
    if slug in SLUG_IMAGE_MAP:
        return SLUG_IMAGE_MAP[slug]
    pool = _resolve_item_type_pool(cat_name, prod_name, slug)
    selector = index if index is not None else zlib.crc32(slug.encode("utf-8"))
    return pool[selector % len(pool)]


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

        meta = next((p for p in PRODUCTS_100 if p["slug"] == slug), None)
        specs = {
            "origin": brand.country_of_origin or "International",
            "demo_notice": "Illustrative demo data",
            "rating": meta["rating"] if meta else 4.8,
            "review_count": meta["review_count"] if meta else 142,
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
                image_url=resolve_seed_image_url(cat_name, prod_name, slug, index=idx),
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
    sync_catalog_120(db, cat_map=cat_map, brand_map=brand_map)

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


def _strip_item_param(url: str | None) -> str:
    if not url:
        return ""
    return re.sub(r"[?&]item=[^&]+", "", url)


def _with_unique_item_param(base_url: str, slug: str, assigned_urls: set[str]) -> str:
    """Return base_url if unassigned, otherwise append a deterministic unique item query param."""
    if base_url not in assigned_urls:
        return base_url
    sep = "&" if "?" in base_url else "?"
    candidate = f"{base_url}{sep}item={slug}"
    counter = 1
    while candidate in assigned_urls:
        candidate = f"{base_url}{sep}item={slug}-{counter}"
        counter += 1
    return candidate


def repair_duplicate_product_images(db: Session) -> int:
    """Repair broken, mismatched, or duplicate ProductImage URLs so every product has a unique matching URL."""
    images = db.query(ProductImage).order_by(ProductImage.product_id, ProductImage.sort_order).all()
    if not images:
        return 0

    prod_map = {p.id: p for p in db.query(Product).all()}
    base_counts: Counter[str] = Counter()
    seen_urls: set[str] = set()
    prev_base: str | None = None
    repaired = 0

    def _is_invalid(url: str | None) -> bool:
        if not url:
            return True
        base = _strip_item_param(url)
        low = base.lower()
        return (
            base in BROKEN_IMAGE_URLS
            or low.endswith(".svg")
            or "placeholder" in low
            or "placehold.co" in low
        )

    for img in images:
        if not _is_invalid(img.image_url):
            base_counts[_strip_item_param(img.image_url)] += 1

    for img in images:
        prod = prod_map.get(img.product_id)
        cat_name = prod.category.name if (prod and prod.category) else "Skincare"
        slug = prod.slug if prod else f"item-{img.id}"
        pool = (
            _resolve_item_type_pool(cat_name, prod.name, prod.slug)
            if prod
            else CATEGORY_IMAGE_POOLS.get(cat_name, VERIFIED_COSMETIC_IMAGE_URLS)
        )

        cur_base = _strip_item_param(img.image_url)
        is_mismatched = _is_invalid(img.image_url) or (cur_base not in pool)
        is_duplicate = img.image_url in seen_urls
        if is_mismatched or is_duplicate:
            unused_bases = [u for u in pool if u not in seen_urls and u != prev_base]
            if unused_bases:
                chosen_base = unused_bases[0]
            else:
                chosen_base = min(
                    [u for u in pool if u != prev_base] or pool,
                    key=lambda u: (base_counts[u], pool.index(u)),
                )
            new_url = _with_unique_item_param(chosen_base, slug, seen_urls)
            if img.image_url and not _is_invalid(img.image_url):
                base_counts[cur_base] = max(0, base_counts[cur_base] - 1)
            img.image_url = new_url
            base_counts[chosen_base] += 1
            seen_urls.add(new_url)
            prev_base = chosen_base
            repaired += 1
        else:
            seen_urls.add(img.image_url)
            prev_base = cur_base

    # Also ensure every product has at least one primary ProductImage
    existing_prod_ids = {img.product_id for img in images}
    for idx, prod in enumerate(prod_map.values(), start=1):
        if prod.id not in existing_prod_ids:
            cat_name = prod.category.name if prod.category else "Skincare"
            pool = _resolve_item_type_pool(cat_name, prod.name, prod.slug)
            unused_bases = [u for u in pool if u not in seen_urls]
            chosen_base = unused_bases[0] if unused_bases else pool[idx % len(pool)]
            new_url = _with_unique_item_param(chosen_base, prod.slug, seen_urls)
            db.add(ProductImage(product_id=prod.id, image_url=new_url, is_primary=True, sort_order=0))
            seen_urls.add(new_url)
            repaired += 1

    if repaired > 0:
        db.commit()
    return repaired


RETIRED_DUPLICATE_SLUGS = {
    "boj-relief-sun-rice-probiotics",
    "lrp-anthelios-invisible-fluid-spf50",
    "round-lab-birch-sun-cream-spf50",
    "olaplex-no3-hair-perfector",
    "olaplex-no-4-shampoo",
    "olaplex-no-5-conditioner",
    "olaplex-no8-moisture-mask",
    "solawave-radiant-renewal-wand",
    "moroccanoil-treatment-original",
    "kerastase-elixir-ultime",
}


def _delete_or_archive_products(db: Session, candidates: list[Product]) -> int:
    """Safely archive products referenced by orders, or delete unreferenced products and dependents."""
    if not candidates:
        return 0
    cleaned = 0
    for prod in candidates:
        variant_ids = [v.id for v in db.query(ProductVariant).filter(ProductVariant.product_id == prod.id).all()]
        has_orders = False
        if variant_ids:
            has_orders = (
                db.query(OrderItem).filter(OrderItem.variant_id.in_(variant_ids)).first()
                is not None
            )

        if has_orders:
            if not prod.is_archived or prod.is_active:
                prod.is_archived = True
                prod.is_active = False
                cleaned += 1
            continue

        if variant_ids:
            db.query(CartItem).filter(CartItem.variant_id.in_(variant_ids)).delete(synchronize_session=False)
            db.query(InventoryMovement).filter(InventoryMovement.variant_id.in_(variant_ids)).delete(synchronize_session=False)
            db.query(InventoryBatch).filter(InventoryBatch.variant_id.in_(variant_ids)).delete(synchronize_session=False)
            db.query(Inventory).filter(Inventory.variant_id.in_(variant_ids)).delete(synchronize_session=False)

        db.query(WishlistItem).filter(WishlistItem.product_id == prod.id).delete(synchronize_session=False)
        db.query(Review).filter(Review.product_id == prod.id).delete(synchronize_session=False)
        db.query(ProductImage).filter(ProductImage.product_id == prod.id).delete(synchronize_session=False)
        db.query(ProductVariant).filter(ProductVariant.product_id == prod.id).delete(synchronize_session=False)
        db.delete(prod)
        cleaned += 1

    if cleaned > 0:
        db.commit()
    return cleaned


def cleanup_generic_generated_products(db: Session) -> int:
    """Remove or archive old generic '#N' and retired duplicate products while keeping orders, users, and carts safe."""
    generic_pattern = re.compile(r" #\d+$")
    candidates = [
        p
        for p in db.query(Product).all()
        if generic_pattern.search(p.name or "") or p.slug in RETIRED_DUPLICATE_SLUGS
    ]
    return _delete_or_archive_products(db, candidates)


def sync_catalog_120(
    db: Session,
    cat_map: dict[str, Category] | None = None,
    brand_map: dict[str, Brand] | None = None,
) -> dict[str, int]:
    """Force-sync the live catalog to the exact 120 distinct products and 120 unique verified images."""
    if cat_map is None or brand_map is None:
        cat_map, brand_map = _ensure_categories_and_brands(db)

    # 1. Remove/archive any old demo/stale products not in PRODUCTS_120 (preserve non-demo admin products)
    stale_candidates = [
        p
        for p in db.query(Product).all()
        if p.is_demo and p.slug not in SLUG_IMAGE_MAP
    ]
    removed = _delete_or_archive_products(db, stale_candidates)

    # 2. Seed any missing products from PRODUCTS_120
    all_blueprint_entries = list(enumerate(CATALOG_BLUEPRINT, start=1))
    created = _seed_blueprint_entries(db, all_blueprint_entries, cat_map, brand_map)

    # 3. Force-refresh metadata and ProductImage URLs for all 120 products
    prod_by_slug = {p.slug: p for p in db.query(Product).all()}
    refreshed_images = 0
    for item in PRODUCTS_120:
        prod = prod_by_slug.get(item["slug"])
        if prod is None:
            continue
        target_cat = cat_map.get(item["category"])
        target_brand = brand_map.get(item["brand"])
        if target_cat and prod.category_id != target_cat.id:
            prod.category_id = target_cat.id
        if target_brand and prod.brand_id != target_brand.id:
            prod.brand_id = target_brand.id
        if prod.name != item["name"]:
            prod.name = item["name"]
        if prod.skin_types != item["skin_types"]:
            prod.skin_types = item["skin_types"]
        if not prod.is_active or prod.is_archived:
            prod.is_active = True
            prod.is_archived = False

        cur_specs = dict(prod.specifications or {})
        if cur_specs.get("rating") != item["rating"] or cur_specs.get("review_count") != item["review_count"]:
            cur_specs["rating"] = item["rating"]
            cur_specs["review_count"] = item["review_count"]
            prod.specifications = cur_specs
            refreshed_images += 1

        existing_imgs = (
            db.query(ProductImage)
            .filter(ProductImage.product_id == prod.id)
            .order_by(ProductImage.sort_order)
            .all()
        )
        exact_url = item["image_url"]
        if len(existing_imgs) == 1 and existing_imgs[0].image_url == exact_url and existing_imgs[0].is_primary:
            continue

        db.query(ProductImage).filter(ProductImage.product_id == prod.id).delete(synchronize_session=False)
        db.add(
            ProductImage(
                product_id=prod.id,
                image_url=exact_url,
                alt_text=item["name"],
                is_primary=True,
                sort_order=0,
            )
        )
        refreshed_images += 1

    if created > 0 or refreshed_images > 0 or removed > 0:
        db.commit()
    return {"removed": removed, "created": created, "refreshed_images": refreshed_images}


sync_catalog_100 = sync_catalog_120


def ensure_initial_data(db: Session) -> bool:
    """Ensure default admin exists and force-sync the 120 distinct products and 120 unique images."""
    ensure_default_admin_and_roles(db)
    stats = sync_catalog_120(db)
    return (stats["removed"] + stats["created"] + stats["refreshed_images"]) > 0


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
        "images": CATEGORY_IMAGE_POOLS["Makeup"],
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
        "images": CATEGORY_IMAGE_POOLS["Skincare"],
    },
    "Sun Care": {
        "items": [
            "Invisible Fluid Sunscreen SPF50+",
            "Tone-Up UV Defense Sun Milk",
            "Hydrating Aloe Sun Gel SPF50",
            "Matte Mineral Sun Stick",
            "Soothing After-Sun Cooling Mist",
        ],
        "images": CATEGORY_IMAGE_POOLS["Sun Care"],
    },
    "Hair Care": {
        "items": [
            "Honey Infused Repair Hair Oil",
            "Keratin Smooth Nourishing Shampoo",
            "Argan Deep Moisture Hair Mask",
            "Heat Protectant Styling Mist",
            "Scalp Revitalizing Tonic",
        ],
        "images": CATEGORY_IMAGE_POOLS["Hair Care"],
    },
    "Fragrance": {
        "items": [
            "Libre Intense Eau De Parfum",
            "Rose Velvet Eau De Toilette",
            "Vanilla Amber Hair & Body Mist",
            "White Peony Botanical Perfume",
        ],
        "images": CATEGORY_IMAGE_POOLS["Fragrance"],
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
    brand = random.choice(BRANDS)
    name = f"{product_base_name} #{index}" if index is not None else product_base_name
    slug_hint = f"{brand}-{name}".lower()
    image_url = resolve_seed_image_url(category_name, name, slug_hint, index=index)
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

            # Primary Real Image (custom image_url or diverse resolved unsplash)
            real_url = item.get("image_url") or resolve_seed_image_url(cat.name, item["name"], slug, index=idx)
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
