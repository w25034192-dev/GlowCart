import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import type { ProductSummary } from '@/types';

const FALLBACK_TRENDING: ProductSummary[] = [
  {
    id: 'fenty-gloss-bomb',
    name: 'Fenty Beauty Gloss Bomb Universal Lip Luminizer',
    slug: 'fenty-gloss-bomb-luminizer',
    category_id: 'cat-makeup',
    category_name: 'Makeup',
    brand_id: 'brand-fenty',
    brand_name: 'Fenty Beauty',
    min_price: '21.00',
    primary_image_url: 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80',
    average_rating: 4.8,
    review_count: 320,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['all'],
  },
  {
    id: 'boj-relief-sun',
    name: 'Beauty of Joseon Relief Sun Rice + Probiotics SPF50+',
    slug: 'beauty-of-joseon-relief-sun',
    category_id: 'cat-suncare',
    category_name: 'Sun Care',
    brand_id: 'brand-boj',
    brand_name: 'Beauty of Joseon',
    min_price: '18.00',
    primary_image_url: '/images/products/art-sunscreen-tube.jpg',
    average_rating: 4.9,
    review_count: 450,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['all', 'sensitive'],
  },
  {
    id: 'cosrx-snail-essence',
    name: 'COSRX Advanced Snail 96 Mucin Power Essence',
    slug: 'cosrx-advanced-snail-96-mucin-power-essence',
    category_id: 'cat-skincare',
    category_name: 'Skincare',
    brand_id: 'brand-cosrx',
    brand_name: 'COSRX',
    min_price: '25.00',
    primary_image_url: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80',
    average_rating: 4.8,
    review_count: 390,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['dry', 'sensitive', 'all'],
  },
  {
    id: 'gisou-hair-oil',
    name: 'Gisou Honey Infused Hair Oil',
    slug: 'gisou-honey-infused-hair-oil',
    category_id: 'cat-haircare',
    category_name: 'Hair Care',
    brand_id: 'brand-gisou',
    brand_name: 'Gisou',
    min_price: '46.00',
    primary_image_url: 'https://images.unsplash.com/photo-1608248597359-58b163351ec1?auto=format&fit=crop&w=800&q=80',
    average_rating: 4.8,
    review_count: 215,
    in_stock: true,
    is_featured: true,
    is_new_arrival: false,
    is_best_seller: true,
    is_demo: false,
    skin_types: ['all'],
  },
];

const SKIN_TONES = [
  {
    id: 'fair',
    label: 'Fair',
    hex: '#F6DFD2',
    matches: [
      { name: 'Petal Pink', shade: '#E58A9B' },
      { name: 'Soft Peony', shade: '#D46A82' },
      { name: 'Nude Blush', shade: '#C98276' },
    ],
  },
  {
    id: 'light',
    label: 'Light',
    hex: '#EBC8B2',
    matches: [
      { name: 'Rosy Day', shade: '#C85A74' },
      { name: 'Warm Rose', shade: '#B84B62' },
      { name: 'Peach Nude', shade: '#C97B68' },
    ],
  },
  {
    id: 'medium',
    label: 'Medium',
    hex: '#D7A382',
    matches: [
      { name: 'Rosy Day', shade: '#BD4265' },
      { name: 'Brick Rose', shade: '#A44638' },
      { name: 'Cinnamon', shade: '#9E4D36' },
    ],
  },
  {
    id: 'tan',
    label: 'Tan',
    hex: '#BA815C',
    matches: [
      { name: 'Spiced Terracotta', shade: '#9C4234' },
      { name: 'Berry Crush', shade: '#8E2846' },
      { name: 'Caramel Kiss', shade: '#8F4D38' },
    ],
  },
  {
    id: 'deep',
    label: 'Deep',
    hex: '#8C583A',
    matches: [
      { name: 'Rich Plum', shade: '#6E223B' },
      { name: 'Mahogany Rose', shade: '#7D3232' },
      { name: 'Espresso Glaze', shade: '#5E2C24' },
    ],
  },
  {
    id: 'rich',
    label: 'Rich',
    hex: '#5E3824',
    matches: [
      { name: 'Velvet Bordeaux', shade: '#59182D' },
      { name: 'Deep Garnet', shade: '#6B1D29' },
      { name: 'Cocoa Berry', shade: '#4F2024' },
    ],
  },
];

export const HomePage: React.FC = () => {
  const [selectedTone, setSelectedTone] = useState(SKIN_TONES[2]); // Default: Medium
  const [trendCategory, setTrendCategory] = useState<string>('all');
  const [products, setProducts] = useState<ProductSummary[]>(FALLBACK_TRENDING);

  // Load products from backend catalog API, filtered by selected trending category
  useEffect(() => {
    const params: Record<string, string | number | boolean | undefined> = {
      page_size: 8,
      sort: 'rating',
    };
    if (trendCategory !== 'all') {
      params.category_slug = trendCategory;
    }
    catalogApi
      .getProducts(params)
      .then((data) => {
        if (data?.items?.length) {
          setProducts(data.items);
        }
      })
      .catch(() => {
        fetch(`/api/catalog/products?limit=8&category_slug=${trendCategory !== 'all' ? trendCategory : ''}`)
          .then((res) => (res.ok ? res.json() : null))
          .then((data) => {
            if (data?.items?.length) {
              setProducts(data.items);
            }
          })
          .catch(() => {});
      });
  }, [trendCategory]);

  return (
    <div className="min-h-screen bg-[#FDF7F8] text-stone-900 font-sans">
      {/* 1. HERO SECTION (Soft Pink Split Layout) */}
      <section className="bg-gradient-to-br from-[#FBECEF] via-[#F7DFE5] to-[#F3D1DA] border-b border-rose-200/50">
        <div className="max-w-7xl mx-auto px-6 py-12 md:py-16 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Left Content */}
          <div className="lg:col-span-6 space-y-6">
            <span className="inline-block text-[11px] font-bold tracking-[0.2em] uppercase text-[#B8295B]">
              NEW • SOFT MATTE RANGE
            </span>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-stone-900 leading-[1.08]">
              Colour That <br />
              <span className="text-[#B8295B]">Feels Like You.</span>
            </h1>

            <p className="text-stone-600 text-base sm:text-lg max-w-md leading-relaxed">
              Creamy, comfortable lipstick &amp; skincare essentials backed by live shade matching and FEFO freshness.
            </p>

            {/* Dual Pill Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Link
                to="/products"
                className="bg-[#B8295B] hover:bg-[#991F4A] text-white font-semibold text-sm px-7 py-3.5 rounded-full shadow-md shadow-rose-900/15 transition-all"
              >
                Shop Cosmetics
              </Link>
              <a
                href="#shade-finder"
                className="bg-white/90 hover:bg-white text-stone-900 border border-stone-300 font-semibold text-sm px-7 py-3.5 rounded-full transition-all"
              >
                Find My Shade
              </a>
            </div>

            {/* Social Proof Avatars */}
            <div className="flex items-center gap-3 pt-2">
              <div className="flex -space-x-2">
                <img
                  src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=80&q=80"
                  alt="Customer"
                  className="w-7 h-7 rounded-full object-cover ring-2 ring-white"
                />
                <img
                  src="https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=80&q=80"
                  alt="Customer"
                  className="w-7 h-7 rounded-full object-cover ring-2 ring-white"
                />
                <img
                  src="https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=80&q=80"
                  alt="Customer"
                  className="w-7 h-7 rounded-full object-cover ring-2 ring-white"
                />
              </div>
              <span className="text-xs font-medium text-stone-600">
                Loved by <strong className="text-stone-900">200,000+</strong> customers
              </span>
            </div>
          </div>

          {/* Right Model Visual + Floating Rating Card */}
          <div className="lg:col-span-6 relative">
            <div className="relative rounded-3xl overflow-hidden shadow-xl bg-rose-200 aspect-[4/3.6]">
              <img
                src="https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=1000&q=85"
                alt="GlowCart Beauty Model"
                className="w-full h-full object-cover"
              />
            </div>

            {/* Floating Rating Badge */}
            <div className="absolute -bottom-4 right-4 sm:right-6 bg-white rounded-2xl px-4 py-3 shadow-lg border border-rose-100 flex items-center gap-2.5">
              <span className="text-amber-400 text-lg">★</span>
              <div>
                <div className="text-xs font-bold text-stone-900">4.8 rating</div>
                <div className="text-[11px] text-stone-500">12k reviews</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. TRUST FEATURE BAR */}
      <div className="bg-white border-b border-rose-100">
        <div className="max-w-6xl mx-auto px-6 py-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-medium text-stone-700">
          <div className="flex items-center justify-center gap-2">
            <span className="text-[#B8295B]">🌿</span> Vegan &amp; Cruelty-Free
          </div>
          <div className="flex items-center justify-center gap-2">
            <span className="text-[#B8295B]">⏱</span> 12-Hour Wear
          </div>
          <div className="flex items-center justify-center gap-2">
            <span className="text-[#B8295B]">💧</span> Hydrating Formula
          </div>
          <div className="flex items-center justify-center gap-2">
            <span className="text-[#B8295B]">↺</span> Free Returns
          </div>
        </div>
      </div>

      {/* 3. TRENDING NOW / VIRAL BEST-SELLERS */}
      <section className="max-w-7xl mx-auto px-6 py-14">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
          <div>
            <span className="text-[11px] font-bold tracking-[0.2em] uppercase text-[#B8295B]">
              TRENDING NOW • BESTSELLERS
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-stone-900 mt-1">
              Viral Best-Sellers &amp; Our Most-Loved Shades
            </h2>
            <p className="text-xs sm:text-sm text-stone-500 mt-1">
              Top-rated formulations and pro beauty rituals loved worldwide with FEFO freshness.
            </p>
          </div>
          <Link
            to={trendCategory === 'all' ? '/catalog' : `/category/${trendCategory}`}
            className="inline-flex items-center text-xs font-semibold text-stone-700 hover:text-[#B8295B] transition-colors"
          >
            Explore All 120 Products →
          </Link>
        </div>

        {/* Category Filter Pills */}
        <div
          className="flex items-center gap-2 overflow-x-auto pb-4 mb-6 scrollbar-none"
          aria-label="Filter trending products by category"
        >
          {[
            { label: 'All Best-Sellers', slug: 'all' },
            { label: 'Makeup', slug: 'makeup' },
            { label: 'Skincare', slug: 'skincare' },
            { label: 'Sun Care', slug: 'sun-care' },
            { label: 'Hair Care', slug: 'hair-care' },
            { label: 'Fragrance', slug: 'fragrance' },
            { label: 'Tools & Brushes', slug: 'beauty-tools' },
          ].map((cat) => {
            const active = trendCategory === cat.slug;
            return (
              <button
                key={cat.slug}
                type="button"
                onClick={() => setTrendCategory(cat.slug)}
                className={`whitespace-nowrap px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                  active
                    ? 'bg-[#B8295B] text-white shadow-sm'
                    : 'bg-white border border-rose-100/80 text-stone-600 hover:border-rose-300 hover:text-stone-900'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>

        {/* Product Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map((item) => (
            <ProductCard key={item.id} product={item} />
          ))}
        </div>
      </section>

      {/* 4. INTERACTIVE SHADE FINDER ("Find Your Perfect Match") */}
      <section
        id="shade-finder"
        className="bg-gradient-to-b from-[#FBECEF] to-[#F6DCE3] py-14 px-6 border-t border-rose-200/50"
      >
        <div className="max-w-3xl mx-auto text-center">
          <span className="text-[11px] font-bold tracking-[0.2em] uppercase text-[#B8295B]">
            SHADE FINDER
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-stone-900 mt-1">
            Find Your Perfect Match
          </h2>
          <p className="text-xs sm:text-sm text-stone-600 mt-1.5">
            Pick your skin tone to see your best shades.
          </p>

          {/* 6 Skin Tone Swatches */}
          <div className="flex flex-wrap justify-center gap-5 sm:gap-7 my-8">
            {SKIN_TONES.map((tone) => {
              const isSelected = selectedTone.id === tone.id;
              return (
                <button
                  key={tone.id}
                  type="button"
                  onClick={() => setSelectedTone(tone)}
                  className="flex flex-col items-center gap-2 group"
                >
                  <span
                    className={`w-11 h-11 rounded-full transition-all ${isSelected
                      ? 'ring-2 ring-offset-2 ring-stone-900 scale-110'
                      : 'hover:scale-105'
                      }`}
                    style={{ backgroundColor: tone.hex }}
                  />
                  <span
                    className={`text-xs ${isSelected ? 'font-bold text-stone-900' : 'text-stone-600'
                      }`}
                  >
                    {tone.label}
                  </span>
                </button>
              );
            })}
          </div>

          {/* 3 Matching Lip/Shade Preview Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
            {selectedTone.matches.map((match) => (
              <div
                key={match.name}
                className="bg-white rounded-2xl p-3 shadow-sm border border-rose-100"
              >
                <div
                  className="h-28 rounded-xl flex items-center justify-center relative overflow-hidden"
                  style={{ backgroundColor: selectedTone.hex }}
                >
                  {/* Lip / Swatch Stroke Visual */}
                  <div
                    className="w-24 h-10 rounded-full shadow-inner opacity-95"
                    style={{ backgroundColor: match.shade }}
                  />
                </div>
                <p className="text-xs font-bold text-stone-900 mt-2.5">{match.name}</p>
              </div>
            ))}
          </div>

          {/* Take the Full Quiz Button */}
          <div className="mt-8">
            <Link
              to="/products"
              className="inline-block bg-[#B8295B] hover:bg-[#991F4A] text-white text-xs font-semibold px-7 py-3 rounded-full shadow-md transition"
            >
              Take the Full Quiz
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
