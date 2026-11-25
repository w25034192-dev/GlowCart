import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, CheckCircle2, ShieldCheck, Sparkles, Truck } from 'lucide-react';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import { Badge, Button, Card } from '@/components/common/UI';

export const HomePage: React.FC = () => {
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterSubscribed, setNewsletterSubscribed] = useState(false);

  const { data: newArrivals } = useQuery({
    queryKey: ['products', 'new_arrival'],
    queryFn: () => catalogApi.getProducts({ new_arrival: true, page_size: 4 }),
  });
  const { data: bestSellers } = useQuery({
    queryKey: ['products', 'best_seller'],
    queryFn: () => catalogApi.getProducts({ best_seller: true, page_size: 4 }),
  });
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: catalogApi.getCategories,
  });
  const { data: brands } = useQuery({
    queryKey: ['brands'],
    queryFn: catalogApi.getBrands,
  });
  const { data: promotions } = useQuery({
    queryKey: ['promotions'],
    queryFn: catalogApi.getPromotions,
  });

  return (
    <div className="space-y-14">
      <section className="overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-blush/70 via-card to-beige p-8 shadow-md sm:p-14">
        <div className="max-w-2xl space-y-6">
          <Badge tone="blush">International Cosmetic Collection · Demo Storefront</Badge>
          <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-6xl">
            Curated Skincare, Shades &amp; Beauty Essentials
          </h1>
          <p className="text-base leading-relaxed text-muted-fg sm:text-lg">
            Explore foundation shades, serums, sunscreens, and hair treatments with transparent
            variant selection and FEFO batch-verified stock availability.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/catalog"
              className="touch-target inline-flex cursor-pointer items-center gap-2 rounded-lg bg-accent px-6 py-3 text-sm font-semibold text-accent-fg shadow-sm transition-opacity duration-200 hover:opacity-90"
            >
              <span>Shop All Cosmetics</span>
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
            <Link
              to="/category/skincare"
              className="touch-target inline-flex cursor-pointer items-center rounded-lg border-2 border-primary bg-card px-6 py-3 text-sm font-semibold text-primary transition-colors duration-200 hover:bg-muted/50"
            >
              Explore Skincare
            </Link>
          </div>
        </div>
      </section>

      <section aria-label="Service highlights" className="grid gap-4 sm:grid-cols-3">
        <Card className="flex items-start gap-3">
          <ShieldCheck className="h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
          <div>
            <h2 className="text-sm font-semibold">Batch &amp; Expiry Checked</h2>
            <p className="text-xs text-muted-fg">FEFO allocation prevents expired stock dispatch.</p>
          </div>
        </Card>
        <Card className="flex items-start gap-3">
          <Sparkles className="h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
          <div>
            <h2 className="text-sm font-semibold">Shade &amp; Volume Precision</h2>
            <p className="text-xs text-muted-fg">Live SKU, HEX swatches, and milliliter sizing.</p>
          </div>
        </Card>
        <Card className="flex items-start gap-3">
          <Truck className="h-6 w-6 shrink-0 text-primary" aria-hidden="true" />
          <div>
            <h2 className="text-sm font-semibold">COD &amp; Sandbox Payments</h2>
            <p className="text-xs text-muted-fg">Server-verified checkout and order tracking.</p>
          </div>
        </Card>
      </section>

      {categories && categories.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-2xl font-bold">Product Collections</h2>
            <Link to="/catalog" className="text-sm font-medium text-primary hover:underline">
              Browse all
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {categories.slice(0, 8).map((cat) => (
              <Link
                key={cat.id}
                to={`/category/${cat.slug}`}
                className="rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary hover:bg-blush/20"
              >
                <div className="font-semibold text-foreground">{cat.name}</div>
                <p className="mt-1 line-clamp-2 text-xs text-muted-fg">
                  {cat.description || 'Explore curated formulas'}
                </p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {newArrivals && newArrivals.items.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-2xl font-bold">New Arrivals</h2>
            <Link to="/catalog?sort=newest" className="text-sm font-medium text-primary hover:underline">
              View more
            </Link>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {newArrivals.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {bestSellers && bestSellers.items.length > 0 && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-2xl font-bold">Best Sellers</h2>
            <Link to="/catalog" className="text-sm font-medium text-primary hover:underline">
              Shop favorites
            </Link>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {bestSellers.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {brands && brands.length > 0 && (
        <section className="space-y-4">
          <h2 className="font-serif text-2xl font-bold">Featured Brands</h2>
          <div className="flex flex-wrap gap-2.5">
            {brands.slice(0, 12).map((b) => (
              <Link
                key={b.id}
                to={`/brand/${b.slug}`}
                className="touch-target inline-flex items-center rounded-full border border-border bg-card px-4 py-2 text-sm font-medium hover:border-primary hover:text-primary"
              >
                {b.name}
              </Link>
            ))}
          </div>
        </section>
      )}

      {promotions && promotions.length > 0 && (
        <section className="rounded-2xl border border-border bg-beige/60 p-6 sm:p-8">
          <h2 className="font-serif text-2xl font-bold">Special Offers</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {promotions.map((promo: { id: string; title: string; description?: string; coupons?: Array<{ code: string }> }) => (
              <Card key={promo.id}>
                <h3 className="text-lg font-semibold text-primary">{promo.title}</h3>
                <p className="mt-1 text-sm text-muted-fg">{promo.description}</p>
                {promo.coupons && promo.coupons.length > 0 && (
                  <p className="mt-3 text-xs">
                    Use code:{' '}
                    <span className="rounded bg-blush px-2 py-1 font-mono font-semibold text-secondary-fg">
                      {promo.coupons[0].code}
                    </span>
                  </p>
                )}
              </Card>
            ))}
          </div>
        </section>
      )}

      <section className="rounded-2xl border border-border bg-card p-6 sm:p-8">
        <div className="mx-auto max-w-xl text-center">
          <h2 className="font-serif text-2xl font-bold">Stay Updated on GlowCart</h2>
          <p className="mt-1 text-sm text-muted-fg">
            Receive skincare guides, new shade launches, and seasonal promotional codes.
          </p>
          {newsletterSubscribed ? (
            <div className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-accent">
              <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
              <span>Subscribed with {newsletterEmail}</span>
            </div>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (newsletterEmail) setNewsletterSubscribed(true);
              }}
              className="mt-4 flex flex-col gap-2 sm:flex-row"
            >
              <label htmlFor="newsletter-email" className="sr-only">
                Email address
              </label>
              <input
                id="newsletter-email"
                type="email"
                required
                value={newsletterEmail}
                onChange={(e) => setNewsletterEmail(e.target.value)}
                placeholder="you@example.com"
                className="flex-1 rounded-lg border border-border px-4 py-2.5 text-sm"
              />
              <Button type="submit">Subscribe</Button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
};

