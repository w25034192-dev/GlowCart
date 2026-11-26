import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  FlaskConical,
  HeartHandshake,
  Leaf,
  Recycle,
  Sparkles,
} from 'lucide-react';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import type { ProductSummary } from '@/types';

const HERO_SLIDES = [
  {
    eyebrow: 'LUXURY GOLDEN SERUM • EDITION',
    headline: 'Radiant Skin. Real Confidence.',
    subtext:
      'Clean, clinically proven beauty curated to nourish and elevate your daily ritual.',
    ctaLabel: 'SHOP NOW',
    ctaTo: '/catalog',
    image:
      'https://images.unsplash.com/photo-1688955665338-fb430ff8436d?auto=format&fit=crop&w=1600&q=85',
    imageAlt:
      'Moody sunlit studio arrangement of luxury golden serum dropper, sleek bottle, and velvet lipsticks',
    featuredTitle: 'Advanced Night Repair Serum',
    featuredPrice: '$85',
    featuredSlug: 'estee-lauder-advanced-night-repair',
    featuredThumb:
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=200&q=80',
  },
  {
    eyebrow: 'HIGH-FASHION MAKEUP EDITORIAL',
    headline: 'Velvet Lips & Luminous Glow.',
    subtext:
      'Runway pigments, silk foundations, and cashmere matte palettes crafted for effortless radiance.',
    ctaLabel: 'SHOP MAKEUP',
    ctaTo: '/category/makeup',
    image:
      'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=1600&q=85',
    imageAlt:
      'Curated luxury makeup flatlay with eyeshadow palette, lipsticks, foundation, and brushes',
    featuredTitle: 'Master Mattes Eyeshadow Palette',
    featuredPrice: '$50',
    featuredSlug: 'makeup-by-mario-master-mattes',
    featuredThumb:
      'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=200&q=80',
  },
  {
    eyebrow: 'HAUTE PARFUMERIE • PARIS',
    headline: 'Signature Scents of Paris.',
    subtext:
      'Artisanal glass flacons and warm amber accords sourced with batch-verified authenticity.',
    ctaLabel: 'SHOP FRAGRANCE',
    ctaTo: '/category/fragrance',
    image:
      'https://images.unsplash.com/photo-1632928145408-ef47a7672964?auto=format&fit=crop&w=1600&q=85',
    imageAlt:
      'Luxury Parisian glass perfume flacon illuminated by warm golden-hour shadows',
    featuredTitle: 'Philosykos Eau de Toilette',
    featuredPrice: '$175',
    featuredSlug: 'diptyque-philosykos-edt',
    featuredThumb:
      'https://images.unsplash.com/photo-1632928145408-ef47a7672964?auto=format&fit=crop&w=200&q=80',
  },
];

const CATEGORY_EDITORIAL_CARDS = [
  {
    label: 'SKINCARE',
    subtitle: 'Dewy Serums & Barrier Creams',
    to: '/category/skincare',
    image:
      'https://images.unsplash.com/photo-1767256046031-743d33937c4e?auto=format&fit=crop&w=900&q=85',
    alt: 'Amber glass skincare serum dropper bottles arranged on warm stone',
  },
  {
    label: 'MAKEUP',
    subtitle: 'Velvet Lips & Luminous Glow',
    to: '/category/makeup',
    image:
      'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=85',
    alt: 'Open eyeshadow palette, blush compact, lipstick, and brushes flatlay',
  },
  {
    label: 'HAIRCARE',
    subtitle: 'Botanical Oils & Silk Repair',
    to: '/category/hair-care',
    image:
      'https://images.unsplash.com/photo-1669281393011-c335050cf0e9?auto=format&fit=crop&w=900&q=85',
    alt: 'Amber glass hair oil dropper bottles on travertine stone',
  },
  {
    label: 'SUN CARE',
    subtitle: 'Weightless SPF & UV Defense',
    to: '/category/sun-care',
    image:
      'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=900&q=85',
    alt: 'Curated sunlit flatlay of SPF skincare tubes and jars',
  },
  {
    label: 'FRAGRANCE',
    subtitle: 'Sculptural Parisian Flacons',
    to: '/category/fragrance',
    image:
      'https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?auto=format&fit=crop&w=900&q=85',
    alt: 'Luxury crystal glass perfume flacon catching warm light',
  },
  {
    label: 'TOOLS & BRUSHES',
    subtitle: 'Pro Brushes & Sculpting Stones',
    to: '/category/beauty-tools',
    image:
      'https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=900&q=85',
    alt: 'Rose-gold makeup brushes, compact, and beauty tools flatlay',
  },
];

const FALLBACK_BEST_SELLERS: ProductSummary[] = [
  {
    id: 'rare-beauty-soft-pinch-blush',
    name: 'Soft Pinch Liquid Blush',
    slug: 'rare-beauty-soft-pinch-blush',
    category_id: 'cat-makeup',
    category_name: 'Makeup',
    brand_id: 'brand-rare',
    brand_name: 'Rare Beauty',
    min_price: '23.00',
    primary_image_url: '/images/products/art-blush-compact.jpg',
    average_rating: 4.8,
    review_count: 424,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['all'],
  },
  {
    id: 'boj-relief-sun',
    name: 'Relief Sun Rice + Probiotics SPF50+',
    slug: 'boj-relief-sun',
    category_id: 'cat-suncare',
    category_name: 'Sun Care',
    brand_id: 'brand-boj',
    brand_name: 'Beauty of Joseon',
    min_price: '18.00',
    primary_image_url: '/images/products/art-sunscreen-tube.jpg',
    average_rating: 4.9,
    review_count: 358,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['all', 'sensitive'],
  },
  {
    id: 'torriden-dive-in-ha-serum',
    name: 'DIVE-IN Hyaluronic Acid Serum',
    slug: 'torriden-dive-in-ha-serum',
    category_id: 'cat-skincare',
    category_name: 'Skincare',
    brand_id: 'brand-torriden',
    brand_name: 'Torriden',
    min_price: '20.00',
    primary_image_url: '/images/products/serum-dropper-hand.jpg',
    average_rating: 4.7,
    review_count: 303,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['dry', 'all'],
  },
  {
    id: 'kerastase-nutritive-8h-magic-night-serum',
    name: 'Nutritive 8H Magic Night Hair Serum',
    slug: 'kerastase-nutritive-8h-magic-night-serum',
    category_id: 'cat-haircare',
    category_name: 'Hair Care',
    brand_id: 'brand-kerastase',
    brand_name: 'Kérastase',
    min_price: '60.00',
    primary_image_url: '/images/products/art-kerastase-magic-night-serum.jpg',
    average_rating: 4.9,
    review_count: 289,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['dry', 'all'],
  },
];

export const HomePage: React.FC = () => {
  const [slideIdx, setSlideIdx] = useState(0);
  const [bestSellers, setBestSellers] = useState<ProductSummary[]>(FALLBACK_BEST_SELLERS);

  useEffect(() => {
    catalogApi
      .getProducts({ page_size: 4, sort: 'rating' })
      .then((data) => {
        if (data?.items?.length) {
          setBestSellers(data.items.slice(0, 4));
        }
      })
      .catch(() => {
        // Keep verified fallback best sellers if API is offline
      });
  }, []);

  const currentSlide = HERO_SLIDES[slideIdx];
  const matchedFeatured = bestSellers.find((p) => p.slug === currentSlide.featuredSlug);
  const featuredHref = matchedFeatured
    ? `/products/${matchedFeatured.id}`
    : `/catalog?q=${encodeURIComponent(currentSlide.featuredTitle)}`;

  const prevSlide = () => setSlideIdx((i) => (i - 1 + HERO_SLIDES.length) % HERO_SLIDES.length);
  const nextSlide = () => setSlideIdx((i) => (i + 1) % HERO_SLIDES.length);

  return (
    <div className="bg-cream-warm text-foreground">
      {/* 2. Full-Bleed Split-Screen Editorial Hero Banner Carousel */}
      <section
        aria-label="Featured beauty collection"
        className="relative overflow-hidden border-b border-border/50 bg-[#F9EFF1]"
      >
        {/* Full-Bleed Right Campaign Image (Desktop) with Soft Left Gradient Blend */}
        <div className="relative h-72 w-full sm:h-96 lg:absolute lg:inset-y-0 lg:right-0 lg:h-full lg:w-[60%]">
          <img
            src={currentSlide.image}
            alt={currentSlide.imageAlt}
            className="h-full w-full object-cover transition-opacity duration-500"
          />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-gradient-to-t from-[#F9EFF1] via-transparent to-transparent lg:bg-gradient-to-r lg:from-[#F9EFF1] lg:via-[#F9EFF1]/45 lg:to-transparent"
          />

          {/* Floating Glassmorphism Featured Product Tag */}
          <Link
            to={featuredHref}
            className="glass-panel group absolute bottom-5 left-5 z-20 flex items-center gap-3.5 rounded-2xl px-4 py-3 shadow-luxury transition-transform duration-200 hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-ring sm:bottom-8 sm:left-8 lg:left-16"
          >
            <img
              src={currentSlide.featuredThumb}
              alt={currentSlide.featuredTitle}
              className="h-11 w-11 rounded-xl border border-white/80 object-cover shadow-sm"
            />
            <div className="text-left">
              <p className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-[0.18em] text-mauve-deep">
                <Sparkles className="h-3 w-3" aria-hidden="true" />
                <span>Featured</span>
              </p>
              <p className="text-xs font-semibold text-plum sm:text-sm">
                {currentSlide.featuredTitle} — <span className="font-mono font-bold">{currentSlide.featuredPrice}</span>
              </p>
            </div>
            <ArrowRight
              className="h-4 w-4 text-plum transition-transform duration-200 group-hover:translate-x-1"
              aria-hidden="true"
            />
          </Link>
        </div>

        {/* Left Editorial Typography & Controls */}
        <div className="relative z-10 mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:py-24">
          <div className="max-w-xl space-y-6">
            <span className="inline-block text-[11px] font-bold uppercase tracking-[0.22em] text-mauve-deep">
              {currentSlide.eyebrow}
            </span>

            <h1 className="font-serif text-4xl font-bold leading-[1.05] tracking-tight text-plum sm:text-5xl lg:text-6xl">
              {currentSlide.headline}
            </h1>

            <p className="max-w-md text-base leading-relaxed text-foreground/80 sm:text-lg">
              {currentSlide.subtext}
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-1">
              <Link
                to={currentSlide.ctaTo}
                className="touch-target inline-flex items-center justify-center rounded-full bg-mauve-deep px-8 py-3.5 text-xs font-bold uppercase tracking-[0.18em] text-white shadow-md transition-colors hover:bg-plum focus-visible:ring-2 focus-visible:ring-ring"
              >
                {currentSlide.ctaLabel}
              </Link>
            </div>

            {/* Subtle Carousel Slide Indicators */}
            <div className="flex items-center gap-2 pt-3" role="tablist" aria-label="Hero slides">
              {HERO_SLIDES.map((s, idx) => (
                <button
                  key={s.headline}
                  type="button"
                  role="tab"
                  aria-selected={idx === slideIdx}
                  aria-label={`Slide ${idx + 1}: ${s.headline}`}
                  onClick={() => setSlideIdx(idx)}
                  className={`h-2.5 rounded-full transition-all duration-200 focus-visible:ring-2 focus-visible:ring-ring ${
                    idx === slideIdx ? 'w-8 bg-plum' : 'w-2.5 bg-mauve/40 hover:bg-mauve'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Edge Carousel Arrows */}
        <button
          type="button"
          onClick={prevSlide}
          aria-label="Previous hero slide"
          className="touch-target absolute left-3 top-36 z-20 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-white/70 bg-card/85 text-plum shadow-md backdrop-blur-md transition-colors hover:bg-card focus-visible:ring-2 focus-visible:ring-ring sm:top-48 lg:left-5 lg:top-1/2"
        >
          <ChevronLeft className="h-5 w-5" aria-hidden="true" />
        </button>
        <button
          type="button"
          onClick={nextSlide}
          aria-label="Next hero slide"
          className="touch-target absolute right-3 top-36 z-20 flex h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-white/70 bg-card/85 text-plum shadow-md backdrop-blur-md transition-colors hover:bg-card focus-visible:ring-2 focus-visible:ring-ring sm:top-48 lg:right-5 lg:top-1/2"
        >
          <ChevronRight className="h-5 w-5" aria-hidden="true" />
        </button>
      </section>

      {/* 3. 4-Column Brand Value / Trust Strip */}
      <section aria-label="Brand values" className="border-b border-border/60 bg-card py-8">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-6 px-4 sm:px-6 lg:grid-cols-4">
          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blush-soft text-mauve-deep">
              <Leaf className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Clean Ingredients</p>
              <p className="text-xs text-muted-fg">Safe &amp; toxin-free</p>
            </div>
          </div>

          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blush-soft text-mauve-deep">
              <FlaskConical className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Clinically Proven</p>
              <p className="text-xs text-muted-fg">Dermatologically tested</p>
            </div>
          </div>

          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blush-soft text-mauve-deep">
              <HeartHandshake className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Cruelty Free</p>
              <p className="text-xs text-muted-fg">Never tested on animals</p>
            </div>
          </div>

          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blush-soft text-mauve-deep">
              <Recycle className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Sustainable Beauty</p>
              <p className="text-xs text-muted-fg">Thoughtfully packaged</p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Shop by Category (6-Column Editorial Arch Portrait Cards) */}
      <section aria-labelledby="shop-by-category-heading" className="mx-auto max-w-7xl px-4 py-14 sm:px-6">
        <div className="text-center">
          <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-mauve-deep">
            CURATED COLLECTIONS
          </p>
          <h2
            id="shop-by-category-heading"
            className="mt-1 font-serif text-3xl font-bold tracking-wide text-plum sm:text-4xl"
          >
            SHOP BY CATEGORY
          </h2>
        </div>

        <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 sm:gap-5 lg:grid-cols-6">
          {CATEGORY_EDITORIAL_CARDS.map((cat) => (
            <Link
              key={cat.label}
              to={cat.to}
              className="group relative flex aspect-[3/4.3] flex-col justify-end overflow-hidden rounded-t-full rounded-b-2xl border border-border/70 bg-card shadow-sm transition-all duration-300 hover:-translate-y-1.5 hover:border-[#c59b27]/70 hover:shadow-[0_18px_36px_-10px_rgba(197,155,39,0.28)] focus-visible:ring-2 focus-visible:ring-ring"
            >
              <img
                src={cat.image}
                alt={cat.alt}
                loading="lazy"
                className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
              />
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 bg-gradient-to-t from-plum/95 via-plum/45 to-transparent transition-opacity duration-300 group-hover:from-plum"
              />
              <div className="relative z-10 flex flex-col items-center p-4 text-center">
                <span className="font-serif text-lg font-bold tracking-wider text-white sm:text-xl">
                  {cat.label}
                </span>
                <span className="mt-0.5 text-[11px] leading-snug text-blush/95">
                  {cat.subtitle}
                </span>
                <span className="mt-3 inline-flex items-center gap-1 rounded-full border border-white/40 bg-white/15 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-white backdrop-blur-md transition-all duration-200 group-hover:border-white group-hover:bg-white group-hover:text-plum">
                  <span>Explore</span>
                  <ArrowRight className="h-3 w-3 transition-transform duration-200 group-hover:translate-x-0.5" aria-hidden="true" />
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 5. Asymmetric Two-Column Promotional Split Banner (~35% Dusty-Mauve / ~65% Flatlay) */}
      <section aria-label="Seasonal promotional offer" className="mx-auto max-w-7xl px-4 pb-14 sm:px-6">
        <div className="grid grid-cols-1 overflow-hidden rounded-3xl border border-border/60 shadow-lg lg:grid-cols-12">
          <div className="flex flex-col justify-center bg-mauve-deep p-8 text-white sm:p-12 lg:col-span-4">
            <span className="text-[11px] font-bold uppercase tracking-[0.22em] text-blush">
              LIMITED TIME OFFER
            </span>
            <h2 className="mt-3 font-serif text-3xl font-bold leading-tight sm:text-4xl">
              Up to 30% Off on Best Sellers
            </h2>
            <p className="mt-4 text-sm leading-relaxed text-white/85">
              Elevate your daily ritual with curated skincare icons, velvet lip colors, and weightless SPF essentials.
            </p>
            <div className="mt-7">
              <Link
                to="/catalog?sort=rating"
                className="touch-target inline-flex items-center justify-center rounded-full bg-card px-7 py-3 text-xs font-bold uppercase tracking-[0.18em] text-plum shadow-sm transition-colors hover:bg-blush-soft focus-visible:ring-2 focus-visible:ring-white"
              >
                SHOP THE SALE
              </Link>
            </div>
          </div>

          <div className="relative min-h-[260px] bg-beige lg:col-span-8 lg:min-h-[380px]">
            <img
              src="https://images.pexels.com/photos/8981523/pexels-photo-8981523.jpeg?auto=compress&cs=tinysrgb&w=1200"
              alt="Curated luxury skincare and fragrance flatlay collection"
              loading="lazy"
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      </section>

      {/* 6. Best Sellers Product Grid (4-Column Card Grid) */}
      <section aria-labelledby="best-sellers-heading" className="mx-auto max-w-7xl px-4 pb-16 sm:px-6">
        <div className="mb-8 flex items-end justify-between border-b border-border/60 pb-4">
          <h2
            id="best-sellers-heading"
            className="font-serif text-3xl font-bold tracking-wide text-plum sm:text-4xl"
          >
            BEST SELLERS
          </h2>
          <Link
            to="/catalog"
            className="touch-target inline-flex items-center text-xs font-bold uppercase tracking-[0.18em] text-mauve-deep transition-colors hover:text-plum"
          >
            VIEW ALL
          </Link>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {bestSellers.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>
    </div>
  );
};
