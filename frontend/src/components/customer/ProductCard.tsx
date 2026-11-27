import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { StarRating } from '@/components/common/UI';
import { cartApi, catalogApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { useToastStore } from '@/store/toastStore';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';
import type { ProductSummary } from '@/types';

export const ProductCard: React.FC<{ product: ProductSummary }> = ({ product }) => {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => Boolean(s.user));
  const setCart = useCartStore((s) => s.setCart);
  const showBagToast = useToastStore((s) => s.showBagToast);

  const [wishlisted, setWishlisted] = useState(false);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

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
      const firstAvailable = detail.variants.find((v) => v.is_available) || detail.variants[0];
      if (!firstAvailable) {
        navigate(`/products/${product.id}`);
        return;
      }
      const updatedCart = await cartApi.addItem(firstAvailable.id, 1);
      setCart(updatedCart);
      setAdded(true);
      showBagToast({
        name: product.name,
        brand: product.brand_name,
        imageUrl: product.primary_image_url,
        price: firstAvailable.price ?? product.min_price,
      });
      setTimeout(() => setAdded(false), 1800);
    } catch {
      navigate(`/products/${product.id}`);
    } finally {
      setAdding(false);
    }
  };

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border border-border/70 bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-mauve/50 hover:shadow-xl">
      <div className="relative aspect-square overflow-hidden bg-cream-warm">
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
            className="flex h-11 w-11 items-center justify-center rounded-full bg-card/95 text-foreground shadow-sm backdrop-blur-sm transition-all duration-200 hover:scale-105 hover:bg-card focus-visible:ring-2 focus-visible:ring-ring"
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
      </div>

      {/* Centered Single Brand Name Title & Full-Width Dusty-Rose ADD TO CART CTA */}
      <div className="flex flex-1 flex-col justify-between p-4 text-center sm:p-5">
        <div className="space-y-1">
          <Link
            to={`/products/${product.id}`}
            className="line-clamp-2 block font-serif text-xl font-bold leading-snug tracking-wide text-plum transition-colors duration-200 hover:text-mauve-deep"
          >
            {product.name || product.brand_name}
          </Link>
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
            className="flex min-h-[44px] w-full items-center justify-center rounded-xl bg-mauve-deep px-4 py-2.5 text-xs font-bold uppercase tracking-[0.16em] text-white transition-colors duration-200 hover:bg-plum focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
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
