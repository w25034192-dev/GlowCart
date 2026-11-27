import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { StarRating } from '@/components/common/UI';
import { cartApi, catalogApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { useToastStore } from '@/store/toastStore';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';
import type { ProductSummary } from '@/types';

interface LuxurySwatch {
  label: string;
  color: string;
}

const CATEGORY_SWATCHES: Record<string, LuxurySwatch[]> = {
  Makeup: [
    { label: 'Velvet Rose', color: '#B55264' },
    { label: 'Cashmere Nude', color: '#C89B86' },
    { label: 'Petal Flush', color: '#D8838E' },
    { label: 'Burgundy Silk', color: '#6E2535' },
  ],
  Skincare: [
    { label: '30 ML', color: '#F3ECE4' },
    { label: '50 ML', color: '#E2D2C0' },
    { label: '100 ML', color: '#C59B27' },
  ],
  Fragrance: [
    { label: '30 ML Eau', color: '#F6E7D8' },
    { label: '50 ML Eau', color: '#E8C594' },
    { label: '100 ML Reserve', color: '#B88940' },
  ],
  'Hair Care': [
    { label: 'Travel 50 ML', color: '#EAD8B1' },
    { label: 'Signature 150 ML', color: '#D4A857' },
    { label: 'Atelier 250 ML', color: '#8F6B32' },
  ],
  'Sun Care': [
    { label: 'Sheer Invisible', color: '#FAF6F0' },
    { label: 'Warm Glow', color: '#E9C9A6' },
    { label: 'Mineral Silk', color: '#D9B18A' },
  ],
  'Beauty Tools': [
    { label: 'Champagne Gold', color: '#D5B26E' },
    { label: 'Rose Quartz', color: '#DF9EA6' },
    { label: 'Obsidian Noir', color: '#292524' },
  ],
};

const CATEGORY_RITUAL_FALLBACK: Record<string, string> = {
  Skincare: 'BOTANICAL ESSENCE • 50 ML',
  Makeup: 'VELVET PIGMENT • STUDIO EDITION',
  Fragrance: 'EAU DE PARFUM • 100 ML',
  'Hair Care': 'SILK ELIXIR • 100 ML',
  'Sun Care': 'BROAD SPECTRUM SPF 50+ • 50 ML',
  'Beauty Tools': 'ATELIER PRO INSTRUMENT',
};

export const ProductCard: React.FC<{ product: ProductSummary }> = ({ product }) => {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => Boolean(s.user));
  const setCart = useCartStore((s) => s.setCart);
  const showBagToast = useToastStore((s) => s.showBagToast);

  const [wishlisted, setWishlisted] = useState(false);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [selectedSwatchIdx, setSelectedSwatchIdx] = useState(0);

  const swatches = useMemo(
    () => CATEGORY_SWATCHES[product.category_name] || CATEGORY_SWATCHES.Skincare,
    [product.category_name]
  );
  const activeSwatch = swatches[selectedSwatchIdx] || swatches[0];

  const ritualText = useMemo(() => {
    const desc = product.short_description?.trim();
    if (desc && desc.includes('•')) {
      return desc.toUpperCase();
    }
    return CATEGORY_RITUAL_FALLBACK[product.category_name] || 'ATELIER ESSENTIAL • SIGNATURE';
  }, [product.short_description, product.category_name]);

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
      const available = detail.variants.filter((v) => v.is_available);
      const chosenVariant =
        available[selectedSwatchIdx] || available[0] || detail.variants[0];
      if (!chosenVariant) {
        navigate(`/products/${product.id}`);
        return;
      }
      const updatedCart = await cartApi.addItem(chosenVariant.id, 1);
      setCart(updatedCart);
      setAdded(true);
      showBagToast({
        name: product.name,
        brand: product.brand_name,
        imageUrl: product.primary_image_url,
        price: chosenVariant.price ?? product.min_price,
      });
      setTimeout(() => setAdded(false), 1800);
    } catch {
      navigate(`/products/${product.id}`);
    } finally {
      setAdding(false);
    }
  };

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border border-stone-200/80 bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-amber-600/40 hover:shadow-xl motion-reduce:transition-none motion-reduce:hover:translate-y-0">
      <div className="relative aspect-square overflow-hidden bg-cream-warm">
        <Link to={`/products/${product.id}`} className="block h-full w-full cursor-pointer">
          <img
            src={resolveMediaUrl(product.primary_image_url, product.name, product.category_name)}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-105 motion-reduce:transition-none motion-reduce:group-hover:scale-100"
            onError={(e) => {
              const target = e.currentTarget;
              if (!target.dataset.fallback) {
                target.dataset.fallback = 'true';
                target.src = getRealFallbackImage(product.name, product.category_name);
              }
            }}
          />
        </Link>

        {/* Top-Left Status Badges (Brand Name is shown cleanly once below the image) */}
        <div className="pointer-events-none absolute left-3 top-3 flex max-w-[calc(100%-4.5rem)] flex-wrap gap-1.5">
          {product.is_best_seller && (
            <span className="inline-flex items-center rounded-full bg-plum/90 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-white shadow-sm backdrop-blur-sm">
              Best Seller
            </span>
          )}
          {hasDiscount && discountPct > 0 && (
            <span className="inline-flex items-center rounded-full bg-rose px-2 py-0.5 font-mono text-[10px] font-bold text-white shadow-sm">
              -{discountPct}%
            </span>
          )}
          {!product.in_stock && (
            <span className="inline-flex items-center rounded-full bg-foreground/90 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-white shadow-sm">
              Sold Out
            </span>
          )}
        </div>

        {/* Floating Wishlist Button (44x44px accessible touch target) */}
        <div className="absolute right-2.5 top-2.5">
          <button
            type="button"
            onClick={handleToggleWishlist}
            aria-label={wishlisted ? `Remove ${product.name} from wishlist` : `Add ${product.name} to wishlist`}
            className="flex h-11 w-11 items-center justify-center rounded-full border border-stone-200/60 bg-white/85 text-foreground shadow-sm backdrop-blur-md transition-all duration-200 hover:scale-105 hover:bg-white focus-visible:ring-2 focus-visible:ring-ring"
          >
            <svg
              viewBox="0 0 24 24"
              className={`h-5 w-5 transition-colors duration-200 ${
                wishlisted ? 'fill-rose text-rose' : 'fill-none text-foreground/80'
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

        {/* Editorial Hover Reveal Strip (Ritual Type & Volume with Champagne-Gold Accent) */}
        <div
          data-testid="editorial-ritual-strip"
          className="pointer-events-none absolute inset-x-3 bottom-3 flex items-center justify-center rounded-xl border border-amber-300/60 bg-white/85 px-3 py-1.5 text-center shadow-sm backdrop-blur-md transition-all duration-300 opacity-0 translate-y-2 group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:translate-y-0 group-focus-within:opacity-100 motion-reduce:transition-none"
        >
          <span
            className="mr-2 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-amber-600"
            aria-hidden="true"
          />
          <span className="truncate text-[10px] font-semibold uppercase tracking-[0.16em] text-stone-800">
            {ritualText}
          </span>
        </div>
      </div>

      {/* Centered Brand Title, Interactive Swatches, Price/Rating & Tactile ADD TO CART CTA */}
      <div className="flex flex-1 flex-col justify-between p-4 text-center sm:p-5">
        <div className="space-y-2.5">
          <Link
            to={`/products/${product.id}`}
            className="line-clamp-2 block font-serif text-lg font-bold uppercase leading-snug tracking-[0.06em] text-plum transition-colors duration-200 hover:text-mauve-deep sm:text-xl"
          >
            {product.name || product.brand_name}
          </Link>

          {/* Subtle Interactive Shade / Size Swatches */}
          <div className="flex flex-col items-center gap-1.5">
            <div className="flex items-center justify-center gap-2" role="group" aria-label="Shade or size options">
              {swatches.map((swatch, idx) => {
                const isSelected = idx === selectedSwatchIdx;
                return (
                  <button
                    key={swatch.label}
                    type="button"
                    aria-label={`Select shade ${swatch.label}`}
                    aria-pressed={isSelected}
                    title={swatch.label}
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setSelectedSwatchIdx(idx);
                    }}
                    className={`h-4 w-4 rounded-full border transition-transform duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 ${
                      isSelected
                        ? 'scale-110 border-plum ring-2 ring-amber-600/60 ring-offset-1'
                        : 'border-stone-300 hover:scale-110'
                    }`}
                    style={{ backgroundColor: swatch.color }}
                  />
                );
              })}
            </div>
            <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-stone-600">
              {activeSwatch.label}
            </span>
          </div>
        </div>

        <div className="mt-4 space-y-3 pt-2">
          <div className="flex flex-col items-center gap-1">
            <div className="flex items-baseline justify-center gap-2 font-mono">
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
            className="flex min-h-[44px] w-full items-center justify-center rounded-xl bg-mauve-deep px-4 py-2.5 text-xs font-bold uppercase tracking-[0.16em] text-white shadow-sm transition-all duration-150 hover:bg-plum active:scale-[0.98] focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          >
            {!product.in_stock
              ? 'Out of Stock'
              : adding
                ? 'Adding...'
                : added
                  ? 'Added to Cart ✓'
                  : 'ADD TO CART'}
          </button>
        </div>
      </div>
    </article>
  );
};
