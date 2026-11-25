import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { catalogApi } from '@/services/api';

interface ProductItem {
  id: string | number;
  name: string;
  finish: string;
  price: number;
  badge?: string;
  image: string;
  swatches: string[];
}

const BESTSELLERS: ProductItem[] = [
  {
    id: 1,
    name: 'Rosy Day',
    finish: 'Soft Matte',
    price: 16,
    image: 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=600&q=80',
    swatches: ['#C86D7C', '#E09A9F', '#9E3E52'],
  },
  {
    id: 2,
    name: 'Berry Crush',
    finish: 'Soft Matte',
    price: 16,
    image: 'https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=600&q=80',
    swatches: ['#9E2A4B', '#C94A6A', '#731C35'],
  },
  {
    id: 3,
    name: 'Nude Silk',
    finish: 'Satin',
    price: 16,
    image: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=600&q=80',
    swatches: ['#C68B77', '#D9A796', '#9C6250'],
  },
  {
    id: 4,
    name: 'Coral Pop',
    finish: 'Gloss',
    price: 14,
    badge: 'New',
    image: 'https://images.unsplash.com/photo-1631214524020-7e18db9a8f92?auto=format&fit=crop&w=600&q=80',
    swatches: ['#E86B63', '#F2948A', '#C4453E'],
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
  const [activeSwatches, setActiveSwatches] = useState<Record<number | string, string>>({});
  const [wishlist, setWishlist] = useState<Record<number | string, boolean>>({});
  const [products, setProducts] = useState<ProductItem[]>(BESTSELLERS);

  // Load products from backend catalog API, falling back to local defaults
  useEffect(() => {
    catalogApi
      .getProducts({ page_size: 4 })
      .then((data) => {
        if (data?.items?.length) {
          const mapped = data.items.slice(0, 4).map((p: any, idx: number) => ({
            id: p.id,
            name: p.name,
            finish: p.category_name || p.category?.name || 'Soft Matte',
            price: Number(p.min_price || p.price || 16),
            badge: idx === 3 ? 'New' : undefined,
            image: p.image_url || p.images?.[0]?.image_url || BESTSELLERS[idx % BESTSELLERS.length].image,
            swatches: BESTSELLERS[idx % BESTSELLERS.length].swatches,
          }));
          setProducts(mapped);
        }
      })
      .catch(() => {
        fetch('/api/catalog/products?limit=4')
          .then((res) => (res.ok ? res.json() : null))
          .then((data) => {
            if (data?.items?.length) {
              const mapped = data.items.slice(0, 4).map((p: any, idx: number) => ({
                id: p.id,
                name: p.name,
                finish: p.category?.name || 'Soft Matte',
                price: Number(p.price || 16),
                badge: idx === 3 ? 'New' : undefined,
                image: p.image_url || BESTSELLERS[idx % BESTSELLERS.length].image,
                swatches: BESTSELLERS[idx % BESTSELLERS.length].swatches,
              }));
              setProducts(mapped);
            }
          })
          .catch(() => {});
      });
  }, []);

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

      {/* 3. BESTSELLERS ("Our Most-Loved Shades") */}
      <section className="max-w-7xl mx-auto px-6 py-14">
        <div className="relative text-center mb-10">
          <span className="text-[11px] font-bold tracking-[0.2em] uppercase text-[#B8295B]">
            BESTSELLERS
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-stone-900 mt-1">
            Our Most-Loved Shades
          </h2>
          <Link
            to="/products"
            className="sm:absolute sm:right-0 sm:bottom-1 inline-block mt-2 sm:mt-0 text-xs font-semibold text-stone-700 hover:text-[#B8295B]"
          >
            View All →
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((item) => {
            const activeColor = activeSwatches[item.id] || item.swatches[0];
            const isLiked = !!wishlist[item.id];

            return (
              <div
                key={item.id}
                className="bg-white rounded-2xl p-3.5 border border-rose-100/80 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
              >
                {/* Product Image Box */}
                <div className="relative rounded-xl overflow-hidden bg-[#F9E8EC] aspect-square mb-3.5">
                  {item.badge && (
                    <span className="absolute top-2.5 left-2.5 bg-[#B8295B] text-white text-[10px] font-bold px-2.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}

                  {/* Heart Wishlist Button */}
                  <button
                    type="button"
                    aria-label={`Wishlist ${item.name}`}
                    onClick={() =>
                      setWishlist((prev) => ({ ...prev, [item.id]: !prev[item.id] }))
                    }
                    className="absolute top-2.5 right-2.5 w-7 h-7 rounded-full bg-white/90 flex items-center justify-center text-xs shadow-sm hover:scale-105 transition"
                  >
                    {isLiked ? '❤️' : '🤍'}
                  </button>

                  <img
                    src={item.image}
                    alt={item.name}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                  />
                </div>

                {/* Shade Swatch Dots */}
                <div className="flex items-center gap-1.5 mb-2">
                  {item.swatches.map((hex) => (
                    <button
                      key={hex}
                      type="button"
                      aria-label={`Select swatch ${hex}`}
                      onClick={() =>
                        setActiveSwatches((prev) => ({ ...prev, [item.id]: hex }))
                      }
                      className={`w-3.5 h-3.5 rounded-full border transition-transform ${
                        activeColor === hex ? 'border-stone-900 scale-125' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: hex }}
                    />
                  ))}
                </div>

                {/* Title & Finish */}
                <Link
                  to={`/products/${item.id}`}
                  className="font-bold text-sm text-stone-900 hover:text-[#B8295B]"
                >
                  {item.name}
                </Link>
                <p className="text-xs text-stone-500">{item.finish}</p>
                <p className="text-sm font-bold text-stone-900 mt-1">${item.price}</p>

                {/* Stars + Add to Bag Pill */}
                <div className="flex items-center justify-between mt-3 pt-2 border-t border-stone-100">
                  <span className="text-amber-400 text-xs tracking-tighter">★★★★★</span>
                  <button
                    type="button"
                    className="bg-stone-900 hover:bg-[#B8295B] text-white text-[11px] font-semibold px-3.5 py-1.5 rounded-full transition-colors"
                  >
                    Add to Bag
                  </button>
                </div>
              </div>
            );
          })}
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
                    className={`w-11 h-11 rounded-full transition-all ${
                      isSelected
                        ? 'ring-2 ring-offset-2 ring-stone-900 scale-110'
                        : 'hover:scale-105'
                    }`}
                    style={{ backgroundColor: tone.hex }}
                  />
                  <span
                    className={`text-xs ${
                      isSelected ? 'font-bold text-stone-900' : 'text-stone-600'
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
