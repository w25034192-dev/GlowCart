import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { StarRating } from '@/components/common/UI';
import { cartApi, catalogApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';
import type { ProductSummary } from '@/types';

const SHADE_SWATCHES_BY_CATEGORY: Record<string, string[]> = {
  Makeup: ['#E8A898', '#C86D7C', '#9E3E52', '#D9B18E'],
  Skincare: ['#F5EDE2', '#E4EFE7'],
  'Sun Care': ['#FAF3E8', '#F2DFC8'],
  'Hair Care': ['#E8C882', '#D6A95C'],
  Fragrance: ['#F3D5D0', '#E5C39B'],
  'Body Care': ['#F4E4D4', '#E5C6AC'],
};

export const ProductCard: React.FC<{ product: ProductSummary }> = ({ product }) => {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => Boolean(s.user));
  const setCart = useCartStore((s) => s.setCart);

  const [wishlisted, setWishlisted] = useState(false);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [selectedSwatchIdx, setSelectedSwatchIdx] = useState(0);

  const hasDiscount =
    product.original_price &&
    product.min_price &&
    Number(product.original_price) > Number(product.min_price);

  const discountPct = hasDiscount
    ? Math.round(
        ((Number(product.original_price) - Number(product.min_price)) /
          Number(product.original_price)) *
          100
      )
    : 0;

  const swatches = SHADE_SWATCHES_BY_CATEGORY[product.category_name] || ['#EBD6C5', '#D6A98F'];

  const handleToggleWishlist = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setWishlisted((prev) => !prev);
    try {
      await cartApi.addWishlist(product.id);
    } catch {
      setWishlisted((prev) => !prev);
    }
  };

  const handleQuickAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!product.in_stock || adding) return;
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    setAdding(true);
    try {
      const detail = await catalogApi.getProduct(product.id);
      const firstAvailable = detail.variants.find((v) => v.is_available) || detail.variants[0];
      if (!firstAvailable) {
        navigate(`/products/${product.id}`);
        return;
      }
      const updatedCart = await cartApi.addItem(firstAvailable.id, 1);
      setCart(updatedCart);
      setAdded(true);
      setTimeout(() => setAdded(false), 1800);
    } catch {
      navigate(`/products/${product.id}`);
    } finally {
      setAdding(false);
    }
  };

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border border-border/80 bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-xl">
      <div className="relative aspect-square overflow-hidden bg-gradient-to-br from-beige/60 via-card to-blush/40">
        <Link to={`/products/${product.id}`} className="block h-full w-full cursor-pointer">
          <img
            src={resolveMediaUrl(product.primary_image_url, product.name, product.category_name)}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-105"
            onError={(e) => {
              const target = e.currentTarget;
              if (!target.dataset.fallback) {
                target.dataset.fallback = 'true';
                target.src = getRealFallbackImage(product.name, product.category_name);
              }
            }}
          />
        </Link>

        {/* Floating Luxury Badges */}
        <div className="pointer-events-none absolute left-3 top-3 flex flex-wrap gap-1.5">
          {product.is_new_arrival && (
            <span className="inline-flex items-center rounded-full bg-card/95 px-2.5 py-0.5 text-[11px] font-semibold tracking-wide text-rose shadow-sm backdrop-blur-sm">
              New
            </span>
          )}
          {product.is_best_seller && (
            <span className="inline-flex items-center rounded-full bg-primary/95 px-2.5 py-0.5 text-[11px] font-semibold tracking-wide text-amber-200 shadow-sm backdrop-blur-sm">
              Best Seller
            </span>
          )}
          {hasDiscount && discountPct > 0 && (
            <span className="inline-flex items-center rounded-full bg-rose-600 px-2 py-0.5 font-mono text-[11px] font-bold text-white shadow-sm">
              -{discountPct}%
            </span>
          )}
          {!product.in_stock && (
            <span className="inline-flex items-center rounded-full bg-slate-900/90 px-2.5 py-0.5 text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
              Sold Out
            </span>
          )}
        </div>

        {/* Floating Wishlist Heart Button (44x44px accessible touch target) */}
        <button
          type="button"
          onClick={handleToggleWishlist}
          aria-label={wishlisted ? `Remove ${product.name} from wishlist` : `Add ${product.name} to wishlist`}
          className="absolute right-2.5 top-2.5 flex h-11 w-11 items-center justify-center rounded-full bg-card/90 text-foreground shadow-sm backdrop-blur-sm transition-all duration-200 hover:scale-105 hover:bg-card focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <svg
            viewBox="0 0 24 24"
            className={`h-5 w-5 transition-colors duration-200 ${
              wishlisted ? 'fill-rose-600 text-rose-600' : 'fill-none text-foreground/80'
            }`}
            stroke="currentColor"
            strokeWidth={1.8}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z"
            />
          </svg>
        </button>
      </div>

      <div className="flex flex-1 flex-col justify-between p-4 sm:p-5">
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted-fg">
            <span className="truncate text-primary">{product.brand_name}</span>
            <span className="shrink-0 text-muted-fg/80">{product.category_name}</span>
          </div>

          <Link
            to={`/products/${product.id}`}
            className="line-clamp-2 block text-sm font-semibold leading-snug text-foreground transition-colors duration-200 hover:text-accent sm:text-base"
          >
            {product.name}
          </Link>

          {/* Shade / Size Preview Dots */}
          <div className="flex items-center gap-1.5 pt-0.5" aria-label="Available finishes">
            {swatches.map((hex, idx) => (
              <button
                key={hex}
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  setSelectedSwatchIdx(idx);
                }}
                aria-label={`Preview variant ${idx + 1}`}
                className={`h-4 w-4 rounded-full border transition-transform duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                  selectedSwatchIdx === idx
                    ? 'scale-110 border-foreground ring-1 ring-foreground/30'
                    : 'border-border/80 hover:scale-105'
                }`}
                style={{ backgroundColor: hex }}
              />
            ))}
            <span className="ml-1 text-[11px] text-muted-fg">
              {product.category_name === 'Makeup' ? 'Shades' : 'Sizes'}
            </span>
          </div>
        </div>

        <div className="mt-4 space-y-3 border-t border-border/50 pt-3">
          <div className="flex items-center justify-between">
            <div className="flex items-baseline gap-2 font-mono">
              <span className="text-base font-bold text-foreground">
                {product.min_price ? `$${Number(product.min_price).toFixed(2)}` : 'N/A'}
              </span>
              {hasDiscount && (
                <span className="text-xs text-muted-fg line-through">
                  ${Number(product.original_price).toFixed(2)}
                </span>
              )}
            </div>
            <StarRating rating={product.average_rating} count={product.review_count} />
          </div>

          <button
            type="button"
            disabled={!product.in_stock || adding}
            onClick={handleQuickAdd}
            className="flex min-h-[44px] w-full items-center justify-center rounded-xl border border-primary/20 bg-primary px-4 py-2 text-xs font-semibold uppercase tracking-wider text-primary-fg transition-all duration-200 hover:bg-primary/90 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          >
            {!product.in_stock
              ? 'Out of Stock'
              : adding
                ? 'Adding...'
                : added
                  ? 'Added to Bag ✓'
                  : 'Quick Add'}
          </button>
        </div>
      </div>
    </article>
  );
};
