import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link, useNavigate } from 'react-router-dom';
import { Check, ShoppingBag, Sparkles, X } from 'lucide-react';
import { StarRating } from '@/components/common/UI';
import { cartApi, catalogApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { useToastStore } from '@/store/toastStore';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';
import type { ProductDetail, ProductSummary, ProductVariant } from '@/types';

interface QuickViewModalProps {
  product: ProductSummary;
  isOpen: boolean;
  onClose: () => void;
}

export const QuickViewModal: React.FC<QuickViewModalProps> = ({ product, isOpen, onClose }) => {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((s) => Boolean(s.user));
  const setCart = useCartStore((s) => s.setCart);
  const showBagToast = useToastStore((s) => s.showBagToast);

  const [detail, setDetail] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    let cancelled = false;
    setLoading(true);
    catalogApi
      .getProduct(product.id)
      .then((res) => {
        if (cancelled) return;
        setDetail(res);
        const first = res.variants.find((v) => v.is_available) || res.variants[0] || null;
        setSelectedVariant(first);
      })
      .catch(() => {
        if (!cancelled) setDetail(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isOpen, product.id]);

  useEffect(() => {
    if (!isOpen) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const activePrice = selectedVariant?.price ?? product.min_price;
  const activeOrigPrice = selectedVariant?.original_price ?? product.original_price;
  const skinTypes = detail?.skin_types?.length ? detail.skin_types : product.skin_types;
  const description =
    detail?.description ||
    product.short_description ||
    `${product.name} by ${product.brand_name}. Curated luxury beauty essential.`;

  const handleAddToBag = async () => {
    if (adding) return;
    if (!isAuthenticated) {
      onClose();
      navigate('/login');
      return;
    }
    const targetVariant =
      selectedVariant ||
      detail?.variants.find((v) => v.is_available) ||
      detail?.variants[0];
    if (!targetVariant) {
      onClose();
      navigate(`/products/${product.id}`);
      return;
    }
    setAdding(true);
    try {
      const updatedCart = await cartApi.addItem(targetVariant.id, 1);
      setCart(updatedCart);
      setAdded(true);
      showBagToast({
        name: product.name,
        brand: product.brand_name,
        imageUrl: product.primary_image_url,
        price: activePrice,
      });
      setTimeout(() => setAdded(false), 1500);
    } finally {
      setAdding(false);
    }
  };

  const handleBackdropClose = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onClose();
  };

  return createPortal(
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby={`qv-title-${product.id}`}
      onClick={handleBackdropClose}
    >
      <div
        className="relative grid max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-border bg-white shadow-2xl md:grid-cols-2"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={handleBackdropClose}
          aria-label="Close quick view"
          className="absolute right-3 top-3 z-10 flex h-11 w-11 items-center justify-center rounded-full bg-white/95 text-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-blush-soft focus-visible:ring-2 focus-visible:ring-ring"
        >
          <X className="h-5 w-5" aria-hidden="true" />
        </button>

        <div className="relative aspect-square bg-gradient-to-br from-beige/60 via-card to-blush/40">
          <img
            src={resolveMediaUrl(product.primary_image_url, product.name, product.category_name)}
            alt={product.name}
            className="h-full w-full object-cover"
            onError={(e) => {
              const target = e.currentTarget;
              if (!target.dataset.fallback) {
                target.dataset.fallback = 'true';
                target.src = getRealFallbackImage(product.name, product.category_name);
              }
            }}
          />
        </div>

        <div className="flex flex-col justify-between p-6 sm:p-7">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-widest text-primary">
              <span>{product.brand_name}</span>
              <span className="text-border">•</span>
              <span className="text-muted-fg">{product.category_name}</span>
            </div>

            <h2
              id={`qv-title-${product.id}`}
              className="font-serif text-2xl font-bold leading-snug text-foreground"
            >
              {product.name}
            </h2>

            <div className="flex items-center justify-between gap-3">
              <div className="flex items-baseline gap-2 font-mono">
                <span className="text-xl font-bold text-foreground">
                  {activePrice ? `$${Number(activePrice).toFixed(2)}` : 'N/A'}
                </span>
                {activeOrigPrice && Number(activeOrigPrice) > Number(activePrice || 0) && (
                  <span className="text-sm text-muted-fg line-through">
                    ${Number(activeOrigPrice).toFixed(2)}
                  </span>
                )}
              </div>
              <StarRating rating={product.average_rating} count={product.review_count} />
            </div>

            <p className="text-sm leading-relaxed text-muted-fg">{description}</p>

            {skinTypes && skinTypes.length > 0 && (
              <div className="space-y-1.5">
                <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-fg">
                  <Sparkles className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                  Skin Type Compatibility
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {skinTypes.map((st) => (
                    <span
                      key={st}
                      className="rounded-full border border-border bg-beige/40 px-2.5 py-0.5 text-xs font-medium capitalize text-foreground"
                    >
                      {st === 'all' ? 'All Skin Types' : st}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {loading ? (
              <div className="h-12 animate-pulse rounded-xl bg-beige/60" />
            ) : (
              detail?.variants &&
              detail.variants.length > 0 && (
                <div className="space-y-2">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-fg">
                    Select Variant
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {detail.variants.map((v) => {
                      const label =
                        v.shade_name ||
                        (v.volume_ml ? `${v.volume_ml}ml` : null) ||
                        v.size ||
                        v.sku;
                      const active = selectedVariant?.id === v.id;
                      return (
                        <button
                          key={v.id}
                          type="button"
                          disabled={!v.is_available}
                          onClick={() => setSelectedVariant(v)}
                          className={`inline-flex min-h-[38px] items-center gap-2 rounded-xl border px-3 py-1.5 text-xs font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                            active
                              ? 'border-primary bg-primary/10 text-primary font-semibold'
                              : 'border-border bg-card text-foreground hover:border-primary/40'
                          } disabled:cursor-not-allowed disabled:opacity-40`}
                        >
                          {v.hex_color && (
                            <span
                              className="h-3.5 w-3.5 rounded-full border border-border/80"
                              style={{ backgroundColor: v.hex_color }}
                            />
                          )}
                          <span>{label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )
            )}
          </div>

          <div className="mt-6 space-y-2.5 border-t border-border/60 pt-4">
            <button
              type="button"
              disabled={!product.in_stock || adding}
              onClick={handleAddToBag}
              className="flex min-h-[44px] w-full items-center justify-center gap-2 rounded-xl bg-mauve-deep px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-white transition-colors hover:bg-plum focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            >
              {added ? (
                <>
                  <Check className="h-4 w-4" aria-hidden="true" />
                  Added to Atelier Bag
                </>
              ) : (
                <>
                  <ShoppingBag className="h-4 w-4" aria-hidden="true" />
                  {!product.in_stock ? 'Out of Stock' : adding ? 'Adding...' : 'Add to Bag'}
                </>
              )}
            </button>
            <Link
              to={`/products/${product.id}`}
              onClick={onClose}
              className="flex min-h-[40px] w-full items-center justify-center rounded-xl border border-border px-4 py-2 text-xs font-semibold uppercase tracking-wider text-foreground transition-colors hover:bg-blush-soft focus-visible:ring-2 focus-visible:ring-ring"
            >
              View Full Product Details
            </Link>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};
