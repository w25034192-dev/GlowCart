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
    ("Bobbi Brown", "bobbi-brown", "USA", True),
    ("Dolce & Gabbana", "dolce-gabbana", "Italy", True),
    ("Kitsch", "kitsch", "USA", True),
    ("Morphe", "morphe", "USA", True),
    ("Olay", "olay", "USA", True),
    ("Urban Decay", "urban-decay", "USA", True),
    ("Versace", "versace", "Italy", True),
    # GlowCart Signature In-House Luxury Maison Lines
    ("GLOWCART LABS", "glowcart-labs", "France", True),
    ("ATELIER VELVET", "atelier-velvet", "France", True),
    ("MAISON LUMIÈRE", "maison-lumiere", "France", True),
    ("SOIE BOTANIQUE", "soie-botanique", "France", True),
    ("SOLEIL PURE", "soleil-pure", "France", True),
    ("ARTISAN PRO", "artisan-pro", "France", True),
    # Verified Pinterest Packaging Brands
    ("CMAYOME", "cmayome", "USA", True),
    ("APRILSKIN", "aprilskin", "South Korea", True),
    ("DR. RASHEL", "dr-rashel", "UAE", True),
    ("Caudalie", "caudalie", "France", True),
    ("BAIPINQIANTIAO", "baipinqiantiao", "France", True),
    ("Schimoni", "schimoni", "Germany", True),
    ("Olivia Garden", "olivia-garden", "Belgium", True),
    ("Stradivarius", "stradivarius", "Spain", True),
    ("FoxyBae", "foxybae", "USA", True),
    ("Salon Line", "salon-line", "Brazil", True),
    ("ghd", "ghd", "UK", True),
    ("KIPOZI", "kipozi", "USA", True),
    ("NOVO", "novo", "South Korea", True),
    ("KAK ELL", "kak-ell", "Malaysia", True),
    ("TRACTA", "tracta", "Brazil", True),
    ("candié", "candie", "France", True),
    ("Balmain Paris", "balmain-paris", "France", True),
    ("Mr.Scrubber", "mr-scrubber", "Ukraine", True),
    ("Vaseline", "vaseline", "USA", True),
    ("Vichy", "vichy", "France", True),
    ("Fairy Skin", "fairy-skin", "Philippines", True),
    ("Surface", "surface", "USA", True),
    ("Louise Young", "louise-young", "UK", True),
    ("MONDAY", "monday", "New Zealand", True),
    ("Pixi", "pixi", "UK", True),
    ("e.l.f.", "elf-cosmetics", "USA", True),
    ("Anastasia Beverly Hills", "anastasia-beverly-hills", "USA", True),
    ("OGX", "ogx", "USA", True),
    ("Kylie Skin", "kylie-skin", "USA", True),
    ("Dr. Althea", "dr-althea", "South Korea", True),
    ("Arencia", "arencia", "South Korea", True),
    ("Cona Lashes", "cona-lashes", "USA", True),
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
    ritual_label = f"{name.upper()} • {size.upper()}"
    return {
        "category": category,
        "brand": brand,
        "name": brand,
        "ritual_label": ritual_label,
        "slug": slug,
        "skin_types": skin_types,
        "variant_template": variant_template,
        "size": size,
        "price": price,
        "image_url": image_url,
        "rating": rating,
        "review_count": review_count,
    }


CURATED_CATALOG: list[dict] = [
    _p('Makeup', 'NARS', 'Light Reflecting Loose Setting Powder', 'pin-01-nars-powder', ['all'], 'shades_powder', '11g', '40.00', '/products/pinterest/pin-01-nars-powder.jpeg'),
    _p('Makeup', 'Maybelline', 'Lash Sensational Full Fan Effect Mascara', 'pin-02-maybelline-mascara', ['all'], 'shades_eye', '9.5ml', '12.99', '/products/pinterest/pin-02-maybelline-mascara.jpeg'),
    _p('Makeup', 'Rhode', 'Peptide Lip Tint', 'pin-03-rhode-lip-tint', ['all'], 'shades_lip', '10ml', '18.00', '/products/pinterest/pin-03-rhode-lip-tint.jpeg'),
    _p('Makeup', 'Yves Saint Laurent', 'Make Me Blush Quilted Powder Blush', 'pin-04-ysl-blush', ['all'], 'shades_blush', '6g', '45.00', '/products/pinterest/pin-04-ysl-blush.jpeg'),
    _p('Beauty Tools', 'CMAYOME', 'Individual Clusters Lashes & Bond Kit', 'pin-05-cmayome-lashes', ['all'], 'sizes', 'Kit', '16.00', '/products/pinterest/pin-05-cmayome-lashes.jpeg'),
    _p('Skincare', 'Anua', 'Heartleaf Pore Control Cleansing Duo', 'pin-06-anua-heartleaf', ['oily', 'sensitive'], 'volumes', '200ml', '26.00', '/products/pinterest/pin-06-anua-heartleaf.jpeg'),
    _p('Skincare', 'APRILSKIN', 'Pink Aloe Pack Cleanser', 'pin-07-aprilskin-cleanser', ['all', 'sensitive'], 'volumes', '120g', '22.00', '/products/pinterest/pin-07-aprilskin-cleanser.jpeg'),
    _p('Sun Care', 'DR. RASHEL', 'Anti-Aging Moisture Sun Cream SPF 60++', 'pin-08-dr-rashel-sun-cream', ['all'], 'volumes', '60g', '14.00', '/products/pinterest/pin-08-dr-rashel-sun-cream.jpeg'),
    _p('Sun Care', 'Caudalie', 'Vinosun Very High Protection Fluid SPF 50+', 'pin-09-caudalie-vinosun', ['all', 'sensitive'], 'volumes', '40ml', '34.00', '/products/pinterest/pin-09-caudalie-vinosun.jpeg'),
    _p('Sun Care', 'Eucerin', 'Pigment Control Sun Fluid SPF 50+', 'pin-10-eucerin-sun-fluid', ['all'], 'volumes', '50ml', '24.00', '/products/pinterest/pin-10-eucerin-sun-fluid.jpeg'),
    _p('Hair Care', "L'Oréal Paris", 'Elvital Glycolic Gloss Shampoo & Conditioner', 'pin-11-loreal-elvital', ['all'], 'volumes', '200ml', '16.00', '/products/pinterest/pin-11-loreal-elvital.jpeg'),
    _p('Fragrance', 'Dior', 'Miss Dior Eau de Parfum', 'pin-12-dior-miss-dior', ['all'], 'volumes', '100ml', '165.00', '/products/pinterest/pin-12-dior-miss-dior.jpeg'),
    _p('Fragrance', 'Valentino', 'Donna Born In Roma Intense', 'pin-13-valentino-born-in-roma', ['all'], 'volumes', '100ml', '170.00', '/products/pinterest/pin-13-valentino-born-in-roma.jpeg'),
    _p('Fragrance', 'Dior', 'Sauvage Parfum', 'pin-14-dior-sauvage', ['all'], 'volumes', '100ml', '185.00', '/products/pinterest/pin-14-dior-sauvage.jpeg'),
    _p('Fragrance', 'Dior', "J'adore Eau de Parfum", 'pin-15-dior-jadore', ['all'], 'volumes', '100ml', '165.00', '/products/pinterest/pin-15-dior-jadore.jpeg'),
    _p('Fragrance', 'Kayali', 'Lovefest Burning Cherry & Vanilla 28', 'pin-16-kayali-cherry-vanilla', ['all'], 'volumes', '50ml', '89.00', '/products/pinterest/pin-16-kayali-cherry-vanilla.jpeg'),
    _p('Fragrance', 'Dior', 'Gris Dior Eau de Parfum', 'pin-17-dior-gris-dior', ['all'], 'volumes', '125ml', '330.00', '/products/pinterest/pin-17-dior-gris-dior.jpeg'),
    _p('Fragrance', 'BAIPINQIANTIAO', 'Ribbed Frosted Glass Fragrance Bottle', 'pin-18-baipinqiantiao-perfume', ['all'], 'volumes', '50ml', '48.00', '/products/pinterest/pin-18-baipinqiantiao-perfume.jpeg'),
    _p('Beauty Tools', 'Schimoni', 'Precision Detail & Art Brush Set', 'pin-19-schimoni-brushes', ['all'], 'sizes', '6-pc Set', '32.00', '/products/pinterest/pin-19-schimoni-brushes.jpeg'),
    _p('Beauty Tools', 'ARTISAN PRO', 'Fine Liner & Detailer Brush Set', 'pin-20-artisan-liner-brushes', ['all'], 'sizes', '5-pc Set', '19.00', '/products/pinterest/pin-20-artisan-liner-brushes.jpeg'),
    _p('Beauty Tools', 'ARTISAN PRO', '3D Sculpture Gel Nail Art Kit', 'pin-21-artisan-sculpture-gel', ['all'], 'sizes', '15ml', '14.00', '/products/pinterest/pin-21-artisan-sculpture-gel.jpeg'),
    _p('Beauty Tools', 'Olivia Garden', 'NanoThermic Ceramic + Ion Hair Brush Set', 'pin-22-olivia-garden-brushes', ['all'], 'sizes', '5-pc Set', '85.00', '/products/pinterest/pin-22-olivia-garden-brushes.jpeg'),
    _p('Beauty Tools', 'Stradivarius', 'Floral Pearl Hair Claw Clip Trio', 'pin-23-stradivarius-clips', ['all'], 'sizes', '3-pc Set', '18.00', '/products/pinterest/pin-23-stradivarius-clips.jpeg'),
    _p('Beauty Tools', 'ARTISAN PRO', 'Satin Sleep Hair Bonnet Duo', 'pin-24-artisan-silk-bonnet', ['all'], 'sizes', '2-pc Set', '24.00', '/products/pinterest/pin-24-artisan-silk-bonnet.jpeg'),
    _p('Beauty Tools', 'Medicube', 'Silicone Scalp & Facial Cleansing Brush', 'pin-25-medicube-cleansing-brush', ['all'], 'sizes', '1 pc', '22.00', '/products/pinterest/pin-25-medicube-cleansing-brush.jpeg'),
    _p('Beauty Tools', 'ARTISAN PRO', 'Exfoliating Bath Loofah Sponge Duo', 'pin-26-artisan-bath-sponge', ['all'], 'sizes', '2-pc Set', '12.00', '/products/pinterest/pin-26-artisan-bath-sponge.jpeg'),
    _p('Beauty Tools', 'FoxyBae', 'Rose Gold Blowout Dryer Brush', 'pin-27-foxybae-dryer-brush', ['all'], 'sizes', 'Device', '69.00', '/products/pinterest/pin-27-foxybae-dryer-brush.jpeg'),
    _p('Beauty Tools', 'Salon Line', 'Lyra Diffuser Hair Dryer', 'pin-28-salon-line-dryer', ['all'], 'sizes', 'Device', '79.00', '/products/pinterest/pin-28-salon-line-dryer.jpeg'),
    _p('Beauty Tools', 'ghd', 'Platinum+ Professional Styler', 'pin-29-ghd-platinum-styler', ['all'], 'sizes', 'Device', '279.00', '/products/pinterest/pin-29-ghd-platinum-styler.jpeg'),
    _p('Beauty Tools', 'KIPOZI', 'Rose Gold Ceramic Curling Iron', 'pin-30-kipozi-curling-iron', ['all'], 'sizes', 'Device', '45.00', '/products/pinterest/pin-30-kipozi-curling-iron.jpeg'),
    _p('Skincare', 'Glow Recipe', 'Watermelon Glow PHA + BHA Toner & Dew Drops', 'pin-31-glow-recipe-toner', ['all', 'dull'], 'volumes', '150ml', '35.00', '/products/pinterest/pin-31-glow-recipe-toner.jpeg'),
    _p('Skincare', 'NOVO', 'Summer Ice Hydrating Gel Mask', 'pin-32-novo-ice-mask', ['all', 'dry'], 'volumes', '100g', '15.00', '/products/pinterest/pin-32-novo-ice-mask.jpeg'),
    _p('Sun Care', 'KAK ELL', 'UV Shield Oil-Free Sunscreen SPF 50', 'pin-33-kak-ell-uv-shield', ['oily', 'all'], 'volumes', '30ml', '19.00', '/products/pinterest/pin-33-kak-ell-uv-shield.jpeg'),
    _p('Makeup', 'TRACTA', 'Contorno Facial Matte Contour Stick', 'pin-34-tracta-contour-stick', ['all'], 'shades_foundation', '12g', '16.00', '/products/pinterest/pin-34-tracta-contour-stick.jpeg'),
    _p('Fragrance', 'candié', 'Pastel Frosted Eau de Parfum Collection', 'pin-35-candie-perfume', ['all'], 'volumes', '50ml', '64.00', '/products/pinterest/pin-35-candie-perfume.jpeg'),
    _p('Beauty Tools', 'Balmain Paris', 'Hair Couture Infrared Blow Dryer', 'pin-36-balmain-dryer', ['all'], 'sizes', 'Device', '245.00', '/products/pinterest/pin-36-balmain-dryer.jpeg'),
    _p('Makeup', 'Chanel', 'Les Beiges Healthy Glow Foundation', 'pin-37-chanel-les-beiges', ['all'], 'shades_foundation', '30ml', '68.00', '/products/pinterest/pin-37-chanel-les-beiges.jpeg'),
    _p('Sun Care', 'Anessa', 'Perfect UV Sunscreen Skincare Milk SPF 50+', 'pin-38-anessa-uv-milk', ['all'], 'volumes', '60ml', '32.00', '/products/pinterest/pin-38-anessa-uv-milk.jpeg'),
    _p('Skincare', 'Beauty of Joseon', 'Ground Rice and Honey Glow Mask', 'pin-39-beauty-of-joseon-mask', ['all', 'dull'], 'volumes', '150ml', '18.00', '/products/pinterest/pin-39-beauty-of-joseon-mask.jpeg'),
    _p('Skincare', 'Mr.Scrubber', 'Bronze Body Shimmer Oil', 'pin-40-mr-scrubber-shimmer', ['all'], 'volumes', '100ml', '21.00', '/products/pinterest/pin-40-mr-scrubber-shimmer.jpeg'),
    _p('Skincare', 'Vaseline', 'Original Healing Jelly', 'pin-41-vaseline-jelly', ['dry', 'all'], 'sizes', '368g', '7.99', '/products/pinterest/pin-41-vaseline-jelly.jpeg'),
    _p('Fragrance', 'Dior', 'Hypnotic Poison Eau de Parfum', 'pin-42-dior-hypnotic-poison', ['all'], 'volumes', '100ml', '160.00', '/products/pinterest/pin-42-dior-hypnotic-poison.jpeg'),
    _p('Sun Care', 'Garnier', 'Vitamin C Wonder Tint SPF 50+', 'pin-43-garnier-vitamin-c-uv', ['all'], 'volumes', '40ml', '16.50', '/products/pinterest/pin-43-garnier-vitamin-c-uv.jpeg'),
    _p('Sun Care', 'Vichy', 'Capital Soleil Invisible Hydrating Milk SPF 50+', 'pin-44-vichy-capital-soleil', ['sensitive', 'all'], 'volumes', '300ml', '34.00', '/products/pinterest/pin-44-vichy-capital-soleil.jpeg'),
    _p('Skincare', 'Garnier', 'SkinActive Hydra Bomb Tissue Mask', 'pin-45-garnier-hydra-bomb', ['dry', 'all'], 'sizes', 'Sheet Mask', '4.99', '/products/pinterest/pin-45-garnier-hydra-bomb.jpeg'),
    _p('Sun Care', 'Fairy Skin', 'Premium Brightening Sunscreen SPF 50', 'pin-46-fairy-skin-sunscreen', ['all'], 'volumes', '50g', '12.00', '/products/pinterest/pin-46-fairy-skin-sunscreen.jpeg'),
    _p('Fragrance', 'Gisou', 'Honey Infused Hair Perfume', 'pin-47-gisou-hair-perfume', ['all'], 'volumes', '50ml', '44.00', '/products/pinterest/pin-47-gisou-hair-perfume.jpeg'),
    _p('Hair Care', 'Gisou', 'Honey Gloss Ceramide Therapy Collection', 'pin-48-gisou-honey-mask', ['dry', 'damaged'], 'volumes', '250ml', '54.00', '/products/pinterest/pin-48-gisou-honey-mask.jpeg'),
    _p('Hair Care', 'Gisou', 'Honey Infused Hair Wash & Oil Routine', 'pin-49-gisou-hair-wash-oil', ['all', 'dry'], 'volumes', '330ml', '48.00', '/products/pinterest/pin-49-gisou-hair-wash-oil.jpeg'),
    _p('Hair Care', 'Surface', 'Awaken Therapeutic Shampoo & Conditioner', 'pin-50-surface-awaken-shampoo', ['thinning', 'all'], 'volumes', '295ml', '36.00', '/products/pinterest/pin-50-surface-awaken-shampoo.jpeg'),
    _p('Beauty Tools', 'Louise Young', 'Professional Makeup Brush Set', 'pin-51-louise-young-brushes', ['all'], 'sizes', '5-pc Set', '72.00', '/products/pinterest/pin-51-louise-young-brushes.jpeg'),
    _p('Makeup', 'ATELIER VELVET', 'Curated Makeup Essentials Bag', 'pin-52-atelier-velvet-kit', ['all'], 'shades_lip', 'Set', '55.00', '/products/pinterest/pin-52-atelier-velvet-kit.jpeg'),
    _p('Makeup', 'Dior', 'Diorshow On Stage Vinyl Black Liner', 'pin-53-dior-vinyl-liner', ['all'], 'shades_eye', '1ml', '34.00', '/products/pinterest/pin-53-dior-vinyl-liner.jpeg'),
    _p('Hair Care', 'MONDAY', 'Moisture Shampoo with Rice Protein', 'pin-54-monday-shampoo', ['dry', 'all'], 'volumes', '350ml', '9.99', '/products/pinterest/pin-54-monday-shampoo.jpeg'),
    _p('Makeup', 'Maybelline', 'Super Stay Lumi-Matte Foundation', 'pin-55-maybelline-superstay', ['all', 'oily'], 'shades_foundation', '35ml', '16.99', '/products/pinterest/pin-55-maybelline-superstay.jpeg'),
    _p('Makeup', 'Pixi', 'On-the-Glow Blush Moisture Stick', 'pin-56-pixi-blush-stick', ['all'], 'shades_blush', '19g', '18.00', '/products/pinterest/pin-56-pixi-blush-stick.jpeg'),
    _p('Beauty Tools', 'ARTISAN PRO', 'Silicone Blending & Nail Art Pens', 'pin-57-artisan-silicone-brushes', ['all'], 'sizes', '2-pc Set', '14.00', '/products/pinterest/pin-57-artisan-silicone-brushes.jpeg'),
    _p('Hair Care', 'Kérastase', 'Gloss Absolu Anti-Frizz Glaze Collection', 'pin-58-kerastase-gloss-absolu', ['all', 'dry'], 'volumes', '250ml', '58.00', '/products/pinterest/pin-58-kerastase-gloss-absolu.jpeg'),
    _p('Fragrance', 'Sol de Janeiro', 'Cheirosa 68 Perfume Mist & Beija Flor Cream', 'pin-59-sol-de-janeiro-68', ['all'], 'volumes', '90ml', '38.00', '/products/pinterest/pin-59-sol-de-janeiro-68.jpeg'),
    _p('Makeup', "L'Oréal Paris", 'True Match Super-Blendable Foundation', 'pin-60-loreal-true-match', ['all'], 'shades_foundation', '30ml', '14.99', '/products/pinterest/pin-60-loreal-true-match.jpeg'),
    _p('Makeup', 'e.l.f.', 'Monochromatic Multi-Stick', 'pin-61-elf-multi-stick', ['all'], 'shades_blush', '4.4g', '5.00', '/products/pinterest/pin-61-elf-multi-stick.jpeg'),
    _p('Skincare', 'CeraVe', 'Daily Moisturizing Lotion', 'pin-62-cerave-lotion', ['dry', 'sensitive'], 'volumes', '355ml', '16.99', '/products/pinterest/pin-62-cerave-lotion.jpeg'),
    _p('Skincare', 'The Ordinary', 'AHA 30% + BHA 2% Peeling Solution', 'pin-63-the-ordinary-peeling', ['oily', 'combination'], 'volumes', '30ml', '9.50', '/products/pinterest/pin-63-the-ordinary-peeling.jpeg'),
    _p('Makeup', 'Marc Jacobs', 'Magic Marc’er Liquid Eyeliner', 'pin-64-marc-jacobs-liner', ['all'], 'shades_eye', '0.5ml', '30.00', '/products/pinterest/pin-64-marc-jacobs-liner.jpeg'),
    _p('Makeup', 'Anastasia Beverly Hills', 'Dipbrow Pomade & Brush #14', 'pin-65-anastasia-dipbrow', ['all'], 'shades_eye', '4g', '21.00', '/products/pinterest/pin-65-anastasia-dipbrow.jpeg'),
    _p('Sun Care', 'CeraVe', 'Hydrating Mineral Sunscreen SPF 50', 'pin-66-cerave-sunscreen', ['sensitive', 'dry'], 'volumes', '150ml', '15.99', '/products/pinterest/pin-66-cerave-sunscreen.jpeg'),
    _p('Sun Care', 'Beauty of Joseon', 'Relief Sun Rice + Probiotics SPF 50+', 'pin-67-beauty-of-joseon-spf', ['all', 'sensitive'], 'volumes', '50ml', '18.00', '/products/pinterest/pin-67-beauty-of-joseon-spf.jpeg'),
    _p('Fragrance', 'Chanel', "N°5 L'Eau Eau de Toilette", 'pin-68-chanel-no5-leau', ['all'], 'volumes', '50ml', '138.00', '/products/pinterest/pin-68-chanel-no5-leau.jpeg'),
    _p('Hair Care', 'OGX', 'Heavenly Hydration Cherry Blossom Shampoo & Conditioner', 'pin-69-ogx-cherry-blossom', ['all', 'dry'], 'volumes', '385ml', '9.99', '/products/pinterest/pin-69-ogx-cherry-blossom.jpeg'),
    _p('Skincare', 'Kylie Skin', 'Detox Clay Face Mask', 'pin-70-kylie-skin-clay-mask', ['oily', 'combination'], 'volumes', '50g', '22.00', '/products/pinterest/pin-70-kylie-skin-clay-mask.jpeg'),
    _p('Skincare', 'Dr. Althea', '345 Relief Cream & Mist', 'pin-71-dr-althea-345', ['sensitive', 'all'], 'volumes', '50ml', '27.00', '/products/pinterest/pin-71-dr-althea-345.jpeg'),
    _p('Skincare', 'Vaseline', 'Gluta-Hya Serum Burst Lotion Dewy Radiance', 'pin-72-vaseline-gluta-hya', ['all', 'dull'], 'volumes', '330ml', '11.50', '/products/pinterest/pin-72-vaseline-gluta-hya.jpeg'),
    _p('Skincare', 'Arencia', 'Fresh Green Rice Mochi Cleanser & Serums', 'pin-73-arencia-rice-cleanser', ['dry', 'sensitive'], 'volumes', '120g', '24.00', '/products/pinterest/pin-73-arencia-rice-cleanser.jpeg'),
    _p('Skincare', 'Laneige', 'Lip Sleeping Mask EX & Lip Glowy Balm', 'pin-74-laneige-lip-mask', ['all', 'dry'], 'sizes', '20g', '24.00', '/products/pinterest/pin-74-laneige-lip-mask.jpeg'),
    _p('Sun Care', 'SKIN1004', 'Madagascar Centella Hyalu-Cica Water-Fit Sun Serum', 'pin-75-skin1004-sun-serum', ['all', 'sensitive'], 'volumes', '50ml', '16.50', '/products/pinterest/pin-75-skin1004-sun-serum.jpeg'),
    _p('Beauty Tools', 'Cona Lashes', 'Gold Precision Eyelash Curler', 'pin-76-cona-lashes-curler', ['all'], 'sizes', '1 pc', '18.00', '/products/pinterest/pin-76-cona-lashes-curler.jpeg'),
    _p('Skincare', 'Garnier', 'SkinActive Micellar Cleansing Water', 'pin-77-garnier-micellar', ['sensitive', 'all'], 'volumes', '400ml', '10.99', '/products/pinterest/pin-77-garnier-micellar.jpeg'),
    _p('Fragrance', 'Gucci', 'Flora Gorgeous Gardenia Eau de Parfum', 'pin-78-gucci-flora', ['all'], 'volumes', '50ml', '135.00', '/products/pinterest/pin-78-gucci-flora.jpeg'),
]

assert len(CURATED_CATALOG) == 78, f"Expected 78 products, got {len(CURATED_CATALOG)}"
assert len({p["image_url"] for p in CURATED_CATALOG}) == 78, "Duplicate image_url in CURATED_CATALOG!"
assert len({p["slug"] for p in CURATED_CATALOG}) == 78, "Duplicate slug in CURATED_CATALOG!"
for p in CURATED_CATALOG:
    assert p["name"] == p["brand"], f"Expected name == brand, got {p['brand']} != {p['name']}"
    assert p["image_url"].startswith("/products/pinterest/")
    assert 4.7 <= p["rating"] <= 4.9
    assert 95 <= p["review_count"] <= 450

# Backwards compatibility aliases
PRODUCTS_100: list[dict] = CURATED_CATALOG
PRODUCTS_120: list[dict] = CURATED_CATALOG

SLUG_IMAGE_MAP: dict[str, str] = {p["slug"]: p["image_url"] for p in CURATED_CATALOG}

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
    if "Beauty Tools" in cat_map:
        cat_map["Tools & Brushes"] = cat_map["Beauty Tools"]

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
    "/products/pinterest/pin-37-chanel-les-beiges.jpeg",
    "/products/pinterest/pin-37-chanel-les-beiges.jpeg",
    "/products/pinterest/pin-03-rhode-lip-tint.jpeg",
    "/products/pinterest/pin-04-ysl-blush.jpeg",
    "/products/pinterest/pin-31-glow-recipe-toner.jpeg",
    "/products/pinterest/pin-03-rhode-lip-tint.jpeg",
    "/products/pinterest/pin-56-pixi-blush-stick.jpeg",
    "/products/pinterest/pin-02-maybelline-mascara.jpeg",
    "/products/pinterest/pin-67-beauty-of-joseon-spf.jpeg",
    "/products/pinterest/pin-39-beauty-of-joseon-mask.jpeg",
    "/products/pinterest/pin-06-anua-heartleaf.jpeg",
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
    "fenty-pro-filtr-soft-matte-foundation": "/products/pinterest/pin-37-chanel-les-beiges.jpeg",
    "fenty-gloss-bomb-luminizer": "/products/pinterest/pin-03-rhode-lip-tint.jpeg",
    "laneige-neo-cushion-matte": "/products/pinterest/pin-04-ysl-blush.jpeg",
    "torriden-dive-in-ha-serum": "/products/pinterest/pin-31-glow-recipe-toner.jpeg",
}

PRODUCT_TYPE_IMAGE_POOLS: dict[str, list[str]] = {
    "foundation_concealer": [
        "/products/pinterest/pin-37-chanel-les-beiges.jpeg",
        "/products/pinterest/pin-37-chanel-les-beiges.jpeg",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "/products/pinterest/pin-04-ysl-blush.jpeg",
    ],
    "blush_powder": [
        "/products/pinterest/pin-56-pixi-blush-stick.jpeg",
        "/products/pinterest/pin-04-ysl-blush.jpeg",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80",
    ],
    "lipstick_gloss": [
        "/products/pinterest/pin-03-rhode-lip-tint.jpeg",
        "/products/pinterest/pin-03-rhode-lip-tint.jpeg",
        "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80",
    ],
    "eye_makeup": [
        "https://images.unsplash.com/photo-1596704017254-9b121068fb31?auto=format&fit=crop&w=800&q=80",
        "/products/pinterest/pin-02-maybelline-mascara.jpeg",
        "https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80",
    ],
    "serum_ampoule": [
        "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
        "/products/pinterest/pin-31-glow-recipe-toner.jpeg",
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
    ],
    "toner_essence": [
        "/products/pinterest/pin-06-anua-heartleaf.jpeg",
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80",
    ],
    "cleanser": [
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "/products/pinterest/pin-06-anua-heartleaf.jpeg",
    ],
    "moisturizer_cream": [
        "/products/pinterest/pin-39-beauty-of-joseon-mask.jpeg",
        "https://images.unsplash.com/photo-1599305090598-fe179d501227?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1656147961287-3f91d30e086e?auto=format&fit=crop&w=800&q=80",
    ],
    "sunscreen": [
        "/products/pinterest/pin-67-beauty-of-joseon-spf.jpeg",
        "/products/pinterest/pin-06-anua-heartleaf.jpeg",
        "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80",
        "/products/pinterest/pin-39-beauty-of-joseon-mask.jpeg",
    ],
    "hair_care": [
        "/products/pinterest/pin-31-glow-recipe-toner.jpeg",
        "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80",
        "/products/pinterest/pin-39-beauty-of-joseon-mask.jpeg",
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
    "carolina-herrera-good-girl",
    "garnier-hair-food-banana-mask",
    "redken-acidic-bonding-concentrate",
    "fino-premium-touch-hair-mask",
    "innisfree-daily-uv-defense",
    "coola-classic-face-sunscreen",
    "eltamd-uv-clear-spf46",
    "anessa-perfect-uv-milk",
}

DEPRECATED_PRODUCT_SKUS = {
    "GC-GARNIER-HAIR-FOOD-BANANA-MASK-V01",
    "GC-079-01",
    "GC-FINO-PREMIUM-TOUCH-HAIR-MASK-V01",
    "GC-058-01",
    "GC-COOLA-CLASSIC-FACE-SUNSCREEN-V01",
    "GC-ELTAMD-UV-CLEAR-SPF46-V01",
    "GC-ANESSA-PERFECT-UV-MILK-V01",
}

DEPRECATED_PRODUCT_NAMES = {
    "carolina herrera good girl",
    "garnier fructis hair food banana mask",
    "redken acidic bonding concentrate",
    "fino premium touch hair mask",
    "innisfree daily uv defense sunscreen",
    "coola classic face sunscreen",
    "eltamd uv clear broad-spectrum spf 46",
    "anessa perfect uv sunscreen skincare milk",
    "anessa perfect uv sunscreen skincare milk spf50+",
}


def purge_deprecated_products(db: Session) -> int:
    """Permanently delete deprecated products and their variants, images, inventory, carts, and wishlists."""
    candidates: list[Product] = []
    seen_ids = set()

    for p in db.query(Product).filter(Product.slug.in_(RETIRED_DUPLICATE_SLUGS)).all():
        if p.id not in seen_ids:
            seen_ids.add(p.id)
            candidates.append(p)

    for v in db.query(ProductVariant).filter(ProductVariant.sku.in_(DEPRECATED_PRODUCT_SKUS)).all():
        if v.product and v.product.id not in seen_ids:
            seen_ids.add(v.product.id)
            candidates.append(v.product)

    for p in db.query(Product).all():
        if p.name and p.name.strip().lower() in DEPRECATED_PRODUCT_NAMES:
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                candidates.append(p)

    return _delete_or_archive_products(db, candidates)


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


def sync_curated_catalog(
    db: Session,
    cat_map: dict[str, Category] | None = None,
    brand_map: dict[str, Brand] | None = None,
) -> dict[str, int]:
    """Force-sync the live catalog to the exact 100 distinct products and 100 unique verified images."""
    if cat_map is None or brand_map is None:
        cat_map, brand_map = _ensure_categories_and_brands(db)

    # 0. Unconditionally purge deprecated / rejected products from PostgreSQL
    purged = purge_deprecated_products(db)

    # 1. Remove/archive any old products not in CURATED_CATALOG (keep ONLY verified Pinterest products)
    stale_candidates = [
        p
        for p in db.query(Product).all()
        if p.slug not in SLUG_IMAGE_MAP or p.slug in RETIRED_DUPLICATE_SLUGS
    ]
    removed = _delete_or_archive_products(db, stale_candidates) + purged

    # 2. Seed any missing products from CURATED_CATALOG
    all_blueprint_entries = list(enumerate(CATALOG_BLUEPRINT, start=1))
    created = _seed_blueprint_entries(db, all_blueprint_entries, cat_map, brand_map)

    # 3. Force-refresh metadata and ProductImage URLs for all 100 products
    prod_by_slug = {p.slug: p for p in db.query(Product).all()}
    refreshed_images = 0
    updated_metadata = 0
    for item in CURATED_CATALOG:
        prod = prod_by_slug.get(item["slug"])
        if prod is None:
            continue
        target_cat = cat_map.get(item["category"])
        target_brand = brand_map.get(item["brand"])
        if target_cat and prod.category_id != target_cat.id:
            prod.category_id = target_cat.id
            updated_metadata += 1
        if target_brand and prod.brand_id != target_brand.id:
            prod.brand_id = target_brand.id
            updated_metadata += 1
        expected_short = item.get("ritual_label") or f"{item['category'].upper()} • {item['size'].upper()}"
        expected_desc = f"{item['name']} — {expected_short}. Authentic formulation with batch-verified freshness."
        if prod.name != item["name"] or prod.short_description != expected_short:
            prod.name = item["name"]
            prod.short_description = expected_short
            prod.description = expected_desc
            updated_metadata += 1
        if prod.skin_types != item["skin_types"]:
            prod.skin_types = item["skin_types"]
            updated_metadata += 1
        if not prod.is_active or prod.is_archived:
            prod.is_active = True
            prod.is_archived = False
            updated_metadata += 1

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

    if created > 0 or refreshed_images > 0 or removed > 0 or updated_metadata > 0:
        db.commit()
    return {
        "removed": removed,
        "created": created,
        "refreshed_images": refreshed_images,
        "updated_metadata": updated_metadata,
    }


sync_catalog_100 = sync_curated_catalog
sync_catalog_120 = sync_curated_catalog


def ensure_initial_data(db: Session) -> bool:
    """Ensure default admin exists and force-sync the 100 distinct products and 100 unique images."""
    ensure_default_admin_and_roles(db)
    stats = sync_curated_catalog(db)
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
