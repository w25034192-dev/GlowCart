import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowRight,
  Award,
  CheckCircle2,
  Droplets,
  Gift,
  HeartHandshake,
  Palette,
  Quote,
  ShieldCheck,
  Sparkles,
  Sun,
  Truck,
  Wind,
} from 'lucide-react';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import { SkinRoutineBuilder } from '@/components/customer/SkinRoutineBuilder';
import { RotatingVideoStudio } from '@/components/customer/RotatingVideoStudio';
import { Badge, Button, Card, StarRating } from '@/components/common/UI';

const CATEGORY_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  makeup: Palette,
  skincare: Droplets,
  'sun-care': Sun,
  'hair-care': Wind,
  'body-care': HeartHandshake,
  fragrance: Sparkles,
  'beauty-tools': Award,
  'makeup-sets': Gift,
};

const COUNTRY_FLAGS: Record<string, string> = {
  Myanmar: '🇲🇲',
  'South Korea': '🇰🇷',
  France: '🇫🇷',
  USA: '🇺🇸',
  Canada: '🇨🇦',
  UK: '🇬🇧',
  UAE: '🇦🇪',
};

const TESTIMONIALS = [
  {
    id: 't-1',
    name: 'Nadia L.',
    skinProfile: 'Combination · Shade 220 Natural Beige',
    rating: 5,
    quote:
      'Being able to see the exact HEX shade swatch, SKU, and non-expired batch availability right on the product page made choosing my foundation effortless.',
  },
  {
    id: 't-2',
    name: 'Hannah K.',
    skinProfile: 'Dry & Sensitive · K-Beauty Routine',
    rating: 5,
    quote:
      'The 30 ml and 50 ml volume selector updates pricing transparently, and every serum arrived sealed with generous shelf-life.',
  },
  {
    id: 't-3',
    name: 'Sora M.',
    skinProfile: 'Oily · Matte Lip & SPF Collector',
    rating: 5,
    quote:
      'Smooth checkout, instant order tracking updates, and thoughtful packaging across skincare and lip shades.',
  },
];

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

  const [brandFilter, setBrandFilter] = useState<'all' | 'local' | 'global'>('all');
  const localBrands = brands?.filter((b) => b.country_of_origin === 'Myanmar') || [];
  const globalBrands = brands?.filter((b) => b.country_of_origin !== 'Myanmar') || [];
  const displayedBrands =
    brandFilter === 'local'
      ? localBrands
      : brandFilter === 'global'
        ? globalBrands
        : brands || [];

  return (
    <div className="space-y-16">
      {/* Luxury Hero Banner with Gradient & Glassmorphism */}
      <section className="relative overflow-hidden rounded-3xl border border-border/80 bg-gradient-to-br from-blush/80 via-beige/70 to-card p-6 shadow-luxury sm:p-12 lg:p-14">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -right-16 -top-16 h-72 w-72 rounded-full bg-blush/80 blur-3xl"
        />
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -bottom-20 left-1/3 h-72 w-72 rounded-full bg-beige blur-3xl"
        />

        <div className="relative z-10 grid gap-8 lg:grid-cols-[1.25fr_0.75fr] lg:items-center">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="blush">International Cosmetic Atelier · Demo Storefront</Badge>
              <span className="inline-flex items-center gap-1 rounded-full bg-card/80 px-2.5 py-0.5 text-[11px] font-semibold text-rose shadow-sm backdrop-blur-sm">
                <Sparkles className="h-3 w-3 text-amber-500" />
                <span>Award-Winning Design</span>
              </span>
            </div>

            <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl leading-[1.1]">
              Curated Skincare, Shades &amp; Beauty Essentials
            </h1>

            <p className="max-w-xl text-base leading-relaxed text-muted-fg sm:text-lg">
              Discover foundation shades, barrier-restoring serums, daily UV shields, and hair
              rituals backed by live variant selection and FEFO batch-verified freshness.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                to="/catalog"
                className="touch-target inline-flex cursor-pointer items-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-sm font-semibold text-primary-fg shadow-md transition-all duration-200 hover:opacity-90 hover:shadow-lg"
              >
                <span>Shop All Cosmetics</span>
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <a
                href="#skin-routine-builder"
                className="touch-target inline-flex cursor-pointer items-center rounded-xl border border-border bg-card/90 px-5 py-3.5 text-sm font-semibold text-primary backdrop-blur-sm transition-all duration-200 hover:border-primary hover:bg-card shadow-sm"
              >
                Build Skin Routine
              </a>
              <a
                href="#rotating-video-studio"
                className="touch-target inline-flex cursor-pointer items-center gap-1.5 rounded-xl border border-rose/30 bg-blush/40 px-4 py-3.5 text-sm font-semibold text-rose backdrop-blur-sm transition-all duration-200 hover:bg-blush shadow-sm"
              >
                <Sparkles className="h-4 w-4" />
                <span>360° Studio</span>
              </a>
            </div>
          </div>

          <div className="rounded-2xl border border-card/90 bg-card/85 p-6 shadow-xl backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-rose">
                GlowCart Beauty Standard
              </span>
              <span className="flex items-center gap-1 font-mono text-[11px] font-bold text-accent">
                <Sparkles className="h-4 w-4 text-accent" aria-hidden="true" />
                <span>VERIFIED</span>
              </span>
            </div>
            <ul className="space-y-3.5 text-sm">
              <li className="flex items-start gap-3">
                <Palette className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                <div>
                  <div className="font-semibold text-foreground">True-to-Tone Shades</div>
                  <p className="text-xs text-muted-fg">Interactive HEX swatches, codes &amp; ml volumes</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                <div>
                  <div className="font-semibold text-foreground">FEFO Freshness Guarantee</div>
                  <p className="text-xs text-muted-fg">Expired cosmetic batches are blocked automatically</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Truck className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                <div>
                  <div className="font-semibold text-foreground">Verified Checkout &amp; Tracking</div>
                  <p className="text-xs text-muted-fg">COD &amp; server-verified sandbox payments</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <Award className="mt-0.5 h-4 w-4 shrink-0 text-accent" aria-hidden="true" />
                <div>
                  <div className="font-semibold text-foreground">Clean &amp; Cruelty-Free Active Curation</div>
                  <p className="text-xs text-muted-fg">Korean Glass Skin, French Luxury &amp; Myanmar Thanakha</p>
                </div>
              </li>
            </ul>
            <div className="border-t border-border/60 pt-2">
              <Link
                to="/category/skincare"
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:text-accent"
              >
                <span>Explore Skincare Collection</span>
                <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Categories Cards with Smooth Hover Transitions */}
      {categories && categories.length > 0 && (
        <section aria-labelledby="featured-categories-heading" className="space-y-5">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-rose">
                Curated Aisles
              </div>
              <h2 id="featured-categories-heading" className="font-serif text-3xl font-bold">
                Featured Categories
              </h2>
            </div>
            <Link
              to="/catalog"
              className="inline-flex items-center gap-1 text-sm font-semibold text-primary hover:text-accent"
            >
              <span>Browse all</span>
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {categories.slice(0, 8).map((cat) => {
              const Icon = CATEGORY_ICONS[cat.slug] || Sparkles;
              return (
                <Link
                  key={cat.id}
                  to={`/category/${cat.slug}`}
                  className="group flex flex-col justify-between rounded-2xl border border-border bg-card p-5 shadow-sm transition-transform transition-shadow duration-200 hover:-translate-y-1 hover:border-primary/40 hover:shadow-md"
                >
                  <div className="flex items-center justify-between">
                    <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-blush/70 text-primary transition-colors duration-200 group-hover:bg-primary group-hover:text-primary-fg">
                      <Icon className="h-5 w-5" aria-hidden="true" />
                    </span>
                    <ArrowRight
                      className="h-4 w-4 text-muted-fg transition-transform duration-200 group-hover:translate-x-1 group-hover:text-primary"
                      aria-hidden="true"
                    />
                  </div>
                  <div className="mt-4">
                    <div className="text-base font-semibold text-foreground">{cat.name}</div>
                    <p className="mt-1 line-clamp-2 text-xs text-muted-fg">
                      {cat.description || 'Explore curated formulas'}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      )}

      {/* Best Sellers Product Showcase */}
      {bestSellers && bestSellers.items.length > 0 && (
        <section aria-labelledby="best-sellers-heading" className="space-y-5">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-rose">
                Community Favorites
              </div>
              <h2 id="best-sellers-heading" className="font-serif text-3xl font-bold">
                Best Sellers
              </h2>
            </div>
            <Link
              to="/catalog?sort=rating"
              className="inline-flex items-center gap-1 text-sm font-semibold text-primary hover:text-accent"
            >
              <span>Shop top rated</span>
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {bestSellers.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {/* Interactive Skin-Type Quiz & Routine Builder */}
      <SkinRoutineBuilder />

      {/* New Arrivals */}
      {newArrivals && newArrivals.items.length > 0 && (
        <section aria-labelledby="new-arrivals-heading" className="space-y-5">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <div className="text-xs font-semibold uppercase tracking-wider text-rose">
                Just Landed
              </div>
              <h2 id="new-arrivals-heading" className="font-serif text-3xl font-bold">
                New Arrivals
              </h2>
            </div>
            <Link
              to="/catalog?sort=newest"
              className="inline-flex items-center gap-1 text-sm font-semibold text-primary hover:text-accent"
            >
              <span>View more</span>
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {newArrivals.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {/* Interactive 360° Rotating Beauty & Short Video Studio */}
      <RotatingVideoStudio />

      {/* Featured & Popular Brands with Local Favorites */}
      {brands && brands.length > 0 && (
        <section aria-labelledby="featured-brands-heading" className="space-y-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-primary">
                Curated Cosmetic Brands
              </p>
              <h2 id="featured-brands-heading" className="font-serif text-3xl font-bold">
                Featured Brands &amp; Local Favorites
              </h2>
              <p className="mt-1 text-sm text-muted-fg">
                Explore iconic international beauty powerhouses alongside authentic Myanmar local skincare and cosmetics.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => setBrandFilter('all')}
                className={`touch-target cursor-pointer rounded-full px-3.5 py-1.5 text-xs font-medium transition-colors ${
                  brandFilter === 'all'
                    ? 'bg-primary text-primary-fg shadow-sm'
                    : 'border border-border bg-card text-foreground hover:bg-blush/30 hover:text-primary'
                }`}
              >
                All Brands ({brands.length})
              </button>
              {localBrands.length > 0 && (
                <button
                  type="button"
                  onClick={() => setBrandFilter('local')}
                  className={`touch-target cursor-pointer rounded-full px-3.5 py-1.5 text-xs font-medium transition-colors ${
                    brandFilter === 'local'
                      ? 'bg-primary text-primary-fg shadow-sm'
                      : 'border border-border bg-card text-foreground hover:bg-blush/30 hover:text-primary'
                  }`}
                >
                  🇲🇲 Myanmar Local ({localBrands.length})
                </button>
              )}
              {globalBrands.length > 0 && (
                <button
                  type="button"
                  onClick={() => setBrandFilter('global')}
                  className={`touch-target cursor-pointer rounded-full px-3.5 py-1.5 text-xs font-medium transition-colors ${
                    brandFilter === 'global'
                      ? 'bg-primary text-primary-fg shadow-sm'
                      : 'border border-border bg-card text-foreground hover:bg-blush/30 hover:text-primary'
                  }`}
                >
                  🌍 Global Icons ({globalBrands.length})
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {displayedBrands.map((b) => {
              const flag = b.country_of_origin ? COUNTRY_FLAGS[b.country_of_origin] || '✨' : '✨';
              const isLocal = b.country_of_origin === 'Myanmar';
              return (
                <Link
                  key={b.id}
                  to={`/brand/${b.slug}`}
                  className="group relative flex flex-col justify-between rounded-xl border border-border bg-card p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/50 hover:shadow-md"
                >
                  <div>
                    <div className="mb-2 flex items-center justify-between text-xs text-muted-fg">
                      <span className="text-base" role="img" aria-label={b.country_of_origin || 'Origin'}>
                        {flag}
                      </span>
                      {isLocal ? (
                        <span className="rounded bg-rose-100 px-1.5 py-0.5 text-[10px] font-semibold text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">
                          Local Gem
                        </span>
                      ) : b.is_featured ? (
                        <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                          Popular
                        </span>
                      ) : null}
                    </div>
                    <span className="block text-sm font-semibold text-foreground transition-colors group-hover:text-primary">
                      {b.name}
                    </span>
                  </div>
                  <span className="mt-3 flex items-center justify-between text-[11px] text-muted-fg transition-colors group-hover:text-primary">
                    <span>{b.country_of_origin || 'Cosmetics'}</span>
                    <ArrowRight className="h-3 w-3 opacity-0 transition-opacity group-hover:opacity-100" />
                  </span>
                </Link>
              );
            })}
          </div>
        </section>
      )}

      {/* Special Offers */}
      {promotions && promotions.length > 0 && (
        <section className="rounded-2xl border border-border bg-beige/60 p-6 sm:p-8">
          <h2 className="font-serif text-3xl font-bold">Special Offers</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {promotions.map(
              (promo: {
                id: string;
                title: string;
                description?: string;
                coupons?: Array<{ code: string }>;
              }) => (
                <Card key={promo.id}>
                  <h3 className="text-lg font-semibold text-primary">{promo.title}</h3>
                  <p className="mt-1 text-sm text-muted-fg">{promo.description}</p>
                  {promo.coupons && promo.coupons.length > 0 && (
                    <p className="mt-3 text-xs text-foreground">
                      Use code:{' '}
                      <span className="rounded bg-blush px-2 py-1 font-mono font-semibold text-foreground">
                        {promo.coupons[0].code}
                      </span>
                    </p>
                  )}
                </Card>
              )
            )}
          </div>
        </section>
      )}

      {/* Customer Testimonials */}
      <section aria-labelledby="testimonials-heading" className="space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-2">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-rose">
              Illustrative Demo Community Feedback
            </div>
            <h2 id="testimonials-heading" className="font-serif text-3xl font-bold">
              Customer Testimonials
            </h2>
          </div>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {TESTIMONIALS.map((item) => (
            <Card
              key={item.id}
              className="flex flex-col justify-between space-y-4 bg-card transition-shadow duration-200 hover:shadow-md"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <StarRating rating={item.rating} />
                  <Quote className="h-5 w-5 text-rose/60" aria-hidden="true" />
                </div>
                <p className="text-sm leading-relaxed text-foreground">&ldquo;{item.quote}&rdquo;</p>
              </div>
              <div className="border-t border-border pt-3">
                <div className="text-sm font-semibold text-foreground">{item.name}</div>
                <div className="text-xs text-muted-fg">{item.skinProfile}</div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Newsletter */}
      <section className="rounded-2xl border border-border bg-gradient-to-r from-card via-beige/50 to-blush/40 p-6 shadow-sm sm:p-10">
        <div className="mx-auto max-w-xl text-center">
          <h2 className="font-serif text-3xl font-bold">Join the GlowCart Atelier List</h2>
          <p className="mt-1 text-sm text-muted-fg">
            Receive skincare ritual guides, new shade launches, and seasonal promotional codes.
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
              className="mt-5 flex flex-col gap-2 sm:flex-row"
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
                className="flex-1 rounded-lg border border-border bg-card px-4 py-2.5 text-sm"
              />
              <Button type="submit">Subscribe</Button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
};
