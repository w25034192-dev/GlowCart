import React from 'react';
import { Link } from 'react-router-dom';
import { Badge, StarRating } from '@/components/common/UI';
import type { ProductSummary } from '@/types';

export const ProductCard: React.FC<{ product: ProductSummary }> = ({ product }) => {
  const hasDiscount =
    product.original_price &&
    product.min_price &&
    Number(product.original_price) > Number(product.min_price);

  return (
    <article className="group flex flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm transition-shadow duration-200 hover:shadow-md">
      <Link
        to={`/products/${product.id}`}
        className="relative block aspect-square cursor-pointer overflow-hidden bg-beige"
      >
        <img
          src={
            product.primary_image_url ||
            `https://placehold.co/500x500/FAF8F6/1C1917?text=${encodeURIComponent(product.name)}`
          }
          alt={product.name}
          loading="lazy"
          className="h-full w-full object-cover"
        />
        <div className="absolute left-3 top-3 flex flex-wrap gap-2">
          {product.is_new_arrival && <Badge tone="blush">New</Badge>}
          {product.is_best_seller && <Badge tone="success">Best Seller</Badge>}
          {!product.in_stock && <Badge tone="danger">Out of Stock</Badge>}
        </div>
      </Link>
      <div className="flex flex-1 flex-col gap-2 p-5">
        <div className="flex items-center justify-between gap-2 text-xs text-muted-fg">
          <span className="font-semibold uppercase tracking-wider">{product.brand_name}</span>
          <span>{product.category_name}</span>
        </div>
        <Link
          to={`/products/${product.id}`}
          className="line-clamp-2 cursor-pointer text-base font-semibold text-foreground transition-colors duration-200 hover:text-accent"
        >
          {product.name}
        </Link>
        <div className="mt-auto flex items-center justify-between pt-2">
          <div className="flex items-baseline gap-2 font-mono">
            <span className="text-base font-semibold text-foreground">
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
