import React from 'react';
import { Link } from 'react-router-dom';
import { StarRating } from '@/components/common/UI';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';
import type { ProductSummary } from '@/types';

export const ProductCard: React.FC<{ product: ProductSummary }> = ({ product }) => {
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

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border border-border/80 bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-lg">
      <Link
        to={`/products/${product.id}`}
        className="relative block aspect-square cursor-pointer overflow-hidden bg-gradient-to-br from-beige/60 via-card to-blush/40"
      >
        <img
          src={resolveMediaUrl(product.primary_image_url, product.name, product.category_name)}
          alt={product.name}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-500 ease-out group-hover:scale-108"
          onError={(e) => {
            const target = e.currentTarget;
            if (!target.dataset.fallback) {
              target.dataset.fallback = 'true';
              target.src = getRealFallbackImage(product.name, product.category_name);
            }
          }}
        />

        {/* Floating Luxury Badges */}
        <div className="absolute left-3 top-3 flex flex-wrap gap-1.5">
          {product.is_new_arrival && (
            <span className="inline-flex items-center rounded-full bg-card/90 px-2.5 py-0.5 text-[11px] font-semibold text-rose shadow-sm backdrop-blur-sm">
              New Arrival
            </span>
          )}
          {product.is_best_seller && (
            <span className="inline-flex items-center rounded-full bg-primary/95 px-2.5 py-0.5 text-[11px] font-semibold text-amber-200 shadow-sm backdrop-blur-sm">
              Best Seller
            </span>
          )}
          {hasDiscount && discountPct > 0 && (
            <span className="inline-flex items-center rounded-full bg-rose-600 px-2 py-0.5 font-mono text-[11px] font-bold text-white shadow-sm">
              -{discountPct}%
            </span>
          )}
          {!product.in_stock && (
            <span className="inline-flex items-center rounded-full bg-slate-800/90 px-2.5 py-0.5 text-[11px] font-semibold text-white shadow-sm backdrop-blur-sm">
              Sold Out
            </span>
          )}
        </div>
      </Link>

      <div className="flex flex-1 flex-col justify-between p-5">
        <div className="space-y-1.5">
          <div className="flex items-center justify-between gap-2 text-[11px] font-semibold uppercase tracking-wider text-muted-fg">
            <span className="truncate text-primary">{product.brand_name}</span>
            <span className="shrink-0 text-muted-fg/80">{product.category_name}</span>
          </div>

          <Link
            to={`/products/${product.id}`}
            className="line-clamp-2 block text-sm font-semibold text-foreground transition-colors duration-200 hover:text-accent sm:text-base leading-snug"
          >
            {product.name}
          </Link>
        </div>

        <div className="mt-4 flex items-center justify-between border-t border-border/50 pt-3">
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
      </div>
    </article>
  );
};
