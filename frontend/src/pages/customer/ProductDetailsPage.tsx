import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Check, Heart, ShieldCheck, ShoppingBag, Sparkles, Truck } from 'lucide-react';
import { cartApi, catalogApi, engagementApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { useToastStore } from '@/store/toastStore';
import { AlertBox, Badge, Button, Card, StarRating } from '@/components/common/UI';
import { ProductCard } from '@/components/customer/ProductCard';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';
import type { ProductVariant } from '@/types';

export const ProductDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const { setCart } = useCartStore();
  const showBagToast = useToastStore((s) => s.showBagToast);

  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState('');

  const [reviewRating, setReviewRating] = useState(5);
  const [reviewTitle, setReviewTitle] = useState('');
  const [reviewComment, setReviewComment] = useState('');

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', id],
    queryFn: () => catalogApi.getProduct(id!),
    enabled: Boolean(id),
  });

  const { data: reviews } = useQuery({
    queryKey: ['reviews', id],
    queryFn: () => engagementApi.getProductReviews(id!),
    enabled: Boolean(id),
  });

  const { data: related } = useQuery({
    queryKey: ['related', product?.category_id],
    queryFn: () => catalogApi.getProducts({ category_id: product?.category_id, page_size: 5 }),
    enabled: Boolean(product?.category_id),
  });

  useEffect(() => {
    if (product?.variants && product.variants.length > 0) {
      setSelectedVariant(product.variants[0]);
    }
  }, [product]);

  if (isLoading || !product) {
    return <div className="py-12 text-center text-muted-fg">Loading product details...</div>;
  }

  const activeVariant = selectedVariant || product.variants[0];
  const discountPct =
    activeVariant?.original_price && Number(activeVariant.original_price) > Number(activeVariant.price)
      ? Math.round(
          ((Number(activeVariant.original_price) - Number(activeVariant.price)) /
            Number(activeVariant.original_price)) *
            100
        )
      : 0;

  const handleAddToCart = async () => {
    setError('');
    setFeedback('');
    if (!user) {
      setError('Please sign in to add items to your shopping cart.');
      return;
    }
    if (!activeVariant) return;
    try {
      const updated = await cartApi.addItem(activeVariant.id, quantity);
      setCart(updated);
      setFeedback(`Added ${product.name} (${activeVariant.shade_name || activeVariant.sku}) to cart.`);
      showBagToast({
        name: product.name,
        brand: product.brand_name,
        imageUrl: product.images[0]?.image_url || product.primary_image_url,
        price: activeVariant.price,
      });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Could not add item to cart.');
    }
  };

  const handleWishlist = async () => {
    if (!user) {
      setError('Please sign in to save products to your wishlist.');
      return;
    }
    await cartApi.addWishlist(product.id);
    setFeedback('Saved to your wishlist.');
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await engagementApi.createReview({
        product_id: product.id,
        rating: reviewRating,
        title: reviewTitle || undefined,
        comment: reviewComment,
      });
      setReviewTitle('');
      setReviewComment('');
      queryClient.invalidateQueries({ queryKey: ['reviews', id] });
      setFeedback('Review submitted.');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Unable to submit review.');
    }
  };

  return (
    <div className="space-y-12">
      <div className="grid gap-10 lg:grid-cols-2">
        <div className="overflow-hidden rounded-2xl border border-border bg-beige">
          <img
            src={resolveMediaUrl(
              product.images[0]?.image_url || product.primary_image_url,
              product.name,
              product.category_name
            )}
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

        <div className="space-y-5">
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-fg">
            <span className="font-semibold uppercase tracking-widest text-primary">
              {product.brand_name}
            </span>
            <span>·</span>
            <span>{product.category_name}</span>
          </div>

          <h1 className="font-serif text-3xl font-bold sm:text-4xl">{product.name}</h1>

          <div className="flex items-center gap-4">
            <StarRating rating={product.average_rating} count={product.review_count} />
            {activeVariant && (
              <span className="font-mono text-xs text-muted-fg">SKU: {activeVariant.sku}</span>
            )}
          </div>

          {activeVariant && (
            <div className="flex items-baseline gap-3 font-mono">
              <span className="text-2xl font-bold text-foreground">
                ${Number(activeVariant.price).toFixed(2)}
              </span>
              {activeVariant.original_price && (
                <span className="text-base text-muted-fg line-through">
                  ${Number(activeVariant.original_price).toFixed(2)}
                </span>
              )}
              {discountPct > 0 && <Badge tone="blush">Save {discountPct}%</Badge>}
              <Badge tone={activeVariant.available_quantity > 0 ? 'success' : 'danger'}>
                {activeVariant.available_quantity > 0
                  ? `${activeVariant.available_quantity} in stock`
                  : 'Out of stock'}
              </Badge>
            </div>
          )}

          <p className="text-sm leading-relaxed text-muted-fg">{product.description}</p>

          {product.variants.length > 0 && (
            <div className="space-y-3 rounded-xl border border-border bg-card p-4">
              <div className="text-sm font-semibold">
                Select Shade / Volume:{' '}
                <span className="text-primary">
                  {activeVariant?.shade_name ||
                    (activeVariant?.volume_ml ? `${activeVariant.volume_ml} ml` : activeVariant?.size || activeVariant?.sku)}
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {product.variants.map((v) => {
                  const isSelected = activeVariant?.id === v.id;
                  const label =
                    v.shade_name || (v.volume_ml ? `${v.volume_ml} ml` : v.size || v.sku);
                  return (
                    <button
                      key={v.id}
                      type="button"
                      onClick={() => setSelectedVariant(v)}
                      aria-pressed={isSelected}
                      className={`touch-target inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors ${
                        isSelected
                          ? 'border-primary bg-blush/40 font-semibold text-foreground'
                          : 'border-border bg-background hover:bg-muted'
                      }`}
                    >
                      {v.hex_color && (
                        <span
                          className="h-4 w-4 rounded-full border border-black/20"
                          style={{ backgroundColor: v.hex_color }}
                          aria-hidden="true"
                        />
                      )}
                      <span>{label}</span>
                      {isSelected && <Check className="h-3.5 w-3.5 text-primary" aria-hidden="true" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {error && <AlertBox message={error} />}
          {feedback && <AlertBox message={feedback} tone="info" />}

          <div className="flex flex-wrap items-center gap-3">
            <label htmlFor="qty-input" className="sr-only">
              Quantity
            </label>
            <input
              id="qty-input"
              type="number"
              min={1}
              max={Math.max(1, activeVariant?.available_quantity || 1)}
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, Number(e.target.value)))}
              className="touch-target w-20 rounded-lg border border-border px-3 py-2 text-center font-mono text-sm"
            />
            <Button
              type="button"
              onClick={handleAddToCart}
              disabled={!activeVariant || activeVariant.available_quantity <= 0}
              className="flex-1"
            >
              <ShoppingBag className="h-4 w-4" aria-hidden="true" />
              <span>Add to Cart</span>
            </Button>
            <Button type="button" variant="outline" onClick={handleWishlist} aria-label="Add to wishlist">
              <Heart className="h-4 w-4" aria-hidden="true" />
            </Button>
          </div>

          {/* Luxury Authenticity & Shipping Badges */}
          <div className="grid gap-2.5 rounded-2xl border border-border/80 bg-gradient-to-br from-beige/50 via-card to-blush/20 p-4 sm:grid-cols-3">
            <div className="flex items-center gap-2.5 text-xs">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <ShieldCheck className="h-4 w-4" aria-hidden="true" />
              </span>
              <div>
                <p className="font-semibold text-foreground">100% Authentic</p>
                <p className="text-[11px] text-muted-fg">Authorized Atelier</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5 text-xs">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Truck className="h-4 w-4" aria-hidden="true" />
              </span>
              <div>
                <p className="font-semibold text-foreground">Free Shipping $75+</p>
                <p className="text-[11px] text-muted-fg">Express Dispatch</p>
              </div>
            </div>
            <div className="flex items-center gap-2.5 text-xs">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
                <Sparkles className="h-4 w-4" aria-hidden="true" />
              </span>
              <div>
                <p className="font-semibold text-foreground">Fresh Batch</p>
                <p className="text-[11px] text-muted-fg">FEFO Verified</p>
              </div>
            </div>
          </div>

          {product.skin_types.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-muted-fg">
                Suitable For:
              </span>
              {product.skin_types.map((st) => (
                <span
                  key={st}
                  className="rounded-full border border-border bg-beige/40 px-3 py-1 text-xs font-medium capitalize text-foreground"
                >
                  {st === 'all' ? 'All Skin Types' : st}
                </span>
              ))}
            </div>
          )}

          {product.verified_ingredients && (
            <Card className="space-y-1.5 text-xs">
              <h2 className="text-sm font-semibold">Key Verified Ingredients</h2>
              <p className="leading-relaxed text-muted-fg">{product.verified_ingredients}</p>
            </Card>
          )}
        </div>
      </div>

      <section className="grid gap-8 lg:grid-cols-2">
        <div className="space-y-4">
          <h2 className="font-serif text-2xl font-bold">Customer Reviews ({reviews?.length ?? 0})</h2>
          {reviews && reviews.length > 0 ? (
            reviews.map((r) => (
              <Card key={r.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{r.author_name}</span>
                  {r.is_verified_purchase && <Badge tone="success">Verified Purchase</Badge>}
                </div>
                <StarRating rating={r.rating} />
                {r.title && <h3 className="text-sm font-semibold">{r.title}</h3>}
                <p className="text-sm text-muted-fg">{r.comment}</p>
              </Card>
            ))
          ) : (
            <p className="text-sm text-muted-fg">No reviews yet. Be the first to review!</p>
          )}
        </div>

        <Card className="h-fit space-y-4">
          <h3 className="font-serif text-xl font-bold">Write a Review</h3>
          <form onSubmit={handleSubmitReview} className="space-y-3">
            <div>
              <label htmlFor="rev-rating" className="block text-sm font-medium">
                Rating (1–5)
              </label>
              <select
                id="rev-rating"
                value={reviewRating}
                onChange={(e) => setReviewRating(Number(e.target.value))}
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm"
              >
                {[5, 4, 3, 2, 1].map((n) => (
                  <option key={n} value={n}>
                    {n} Stars
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="rev-title" className="block text-sm font-medium">
                Headline
              </label>
              <input
                id="rev-title"
                type="text"
                value={reviewTitle}
                onChange={(e) => setReviewTitle(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="rev-comment" className="block text-sm font-medium">
                Review
              </label>
              <textarea
                id="rev-comment"
                required
                rows={3}
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
              />
            </div>
            <Button type="submit" disabled={!user}>
              {user ? 'Submit Review' : 'Sign in to Review'}
            </Button>
          </form>
        </Card>
      </section>

      {related && related.items.filter((p) => p.id !== product.id).length > 0 && (
        <section className="space-y-5 border-t border-border/60 pt-10">
          <div className="space-y-1">
            <p className="text-[11px] font-semibold uppercase tracking-widest text-primary">
              Atelier Pairing
            </p>
            <h2 className="font-serif text-2xl font-bold sm:text-3xl">
              Complete Your Routine · You May Also Like
            </h2>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {related.items
              .filter((p) => p.id !== product.id)
              .slice(0, 4)
              .map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
          </div>
        </section>
      )}
    </div>
  );
};

