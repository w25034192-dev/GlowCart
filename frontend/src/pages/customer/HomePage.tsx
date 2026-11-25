import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, CheckCircle2, Quote } from 'lucide-react';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import { SkinRoutineBuilder } from '@/components/customer/SkinRoutineBuilder';
import { Button, Card, StarRating } from '@/components/common/UI';

const SHADE_PRESETS = [
  { name: '01 Ivory Silk (Cool Undertone)', color: '#F3D6BE' },
  { name: '02 Warm Honey (Neutral)', color: '#E5B88E' },
  { name: '03 Golden Amber (Warm)', color: '#C88E62' },
  { name: '04 Rich Espresso (Deep)', color: '#8D5534' },
];

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
  const [activeShadeIndex, setActiveShadeIndex] = useState(0);
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterSubscribed, setNewsletterSubscribed] = useState(false);

  const activeShade = SHADE_PRESETS[activeShadeIndex] || SHADE_PRESETS[0];

  const { data: newArrivals } = useQuery({
    queryKey: ['products', 'new_arrival'],
    queryFn: () => catalogApi.getProducts({ new_arrival: true, page_size: 4 }),
  });
  const { data: bestSellers } = useQuery({
    queryKey: ['products', 'best_seller'],
    queryFn: () => catalogApi.getProducts({ best_seller: true, page_size: 4 }),
  });
  const { data: promotions } = useQuery({
    queryKey: ['promotions'],
    queryFn: catalogApi.getPromotions,
  });

  return (
    <div className="space-y-16">
      {/* Hero Section — Split & Glassmorphism with Live Serum Orb */}
      <section className="grid items-center gap-8 lg:grid-cols-[1.2fr_0.8fr]">
        <div>
          <span className="eyebrow mb-3.5 inline-block text-[11px] font-semibold uppercase tracking-[2px] text-[#B86B43]">
            International Cosmetic Atelier
          </span>
          <h1 className="font-serif text-4xl font-bold leading-[1.05] tracking-tight text-foreground sm:text-5xl lg:text-6xl mb-5">
            Curated Skincare, Shades &amp; <em className="italic text-[#B86B43]">Beauty Essentials</em>
          </h1>
          <p className="max-w-xl text-base leading-relaxed text-muted-fg mb-7">
            Discover foundation shades, barrier-restoring serums, and daily UV shields backed by
            live variant selection and FEFO batch-verified freshness.
          </p>
          <div className="flex flex-wrap gap-3.5">
            <Link
              to="/catalog"
              className="touch-target inline-flex cursor-pointer items-center gap-2 rounded-xl bg-[#B86B43] px-6 py-3.5 text-sm font-semibold text-white shadow-sm transition-all duration-200 hover:bg-[#9A5532] hover:-translate-y-0.5"
            >
              <span>Shop All Cosmetics →</span>
            </Link>
            <a
              href="#skin-routine-builder"
              className="touch-target inline-flex cursor-pointer items-center rounded-xl border border-foreground/80 bg-transparent px-6 py-3.5 text-sm font-semibold text-foreground transition-colors duration-200 hover:bg-foreground/5"
            >
              Build Skin Routine
            </a>
          </div>
        </div>

        {/* Interactive Shade Matcher Card */}
        <div className="hero-visual">
          <div className="text-[12px] font-semibold tracking-wider text-[#1C1B1A]">
            LIVE SHADE PREVIEW
          </div>
          <div
            className="serum-orb"
            id="shadeOrb"
            style={{ backgroundColor: activeShade.color }}
          />
          <div className="glass-widget">
            <div className="widget-header">
              <span className="text-foreground">True-to-Tone Finder</span>
              <span className="font-semibold text-[#B86B43]">FEFO Verified ✓</span>
            </div>
            <div className="swatches">
              {SHADE_PRESETS.map((preset, idx) => (
                <button
                  key={preset.name}
                  type="button"
                  onClick={() => setActiveShadeIndex(idx)}
                  className={`swatch ${activeShadeIndex === idx ? 'active' : ''}`}
                  style={{ backgroundColor: preset.color }}
                  aria-label={`Select shade ${preset.name}`}
                  title={preset.name}
                />
              ))}
            </div>
            <div className="shade-label font-medium text-xs sm:text-sm" id="shadeName">
              Selected: {activeShade.name}
            </div>
          </div>
        </div>
      </section>

      {/* Infinite Marquee */}
      <div className="marquee-wrap" aria-hidden="true">
        <div className="marquee-track">
          ✦ FEFO BATCH-VERIFIED FRESHNESS &nbsp;&nbsp;&nbsp; ✦ LIVE HEX SHADE MATCHING &nbsp;&nbsp;&nbsp; ✦ DERMATOLOGIST TESTED &nbsp;&nbsp;&nbsp; ✦ VERIFIED CHECKOUT &amp; TRACKING &nbsp;&nbsp;&nbsp;
          ✦ FEFO BATCH-VERIFIED FRESHNESS &nbsp;&nbsp;&nbsp; ✦ LIVE HEX SHADE MATCHING &nbsp;&nbsp;&nbsp; ✦ DERMATOLOGIST TESTED &nbsp;&nbsp;&nbsp; ✦ VERIFIED CHECKOUT &amp; TRACKING &nbsp;&nbsp;&nbsp;
        </div>
      </div>

      {/* Bento Grid Categories */}
      <section className="space-y-6" id="categories" aria-labelledby="featured-categories-heading">
        <div className="flex items-end justify-between">
          <div>
            <span className="bento-tag">Curated Aisles</span>
            <h2 id="featured-categories-heading" className="font-serif text-3xl font-bold sm:text-4xl">
              Featured Categories
            </h2>
          </div>
          <Link
            to="/catalog"
            className="text-sm font-semibold text-[#1C1B1A] transition-colors hover:text-[#B86B43]"
          >
            Browse all +
          </Link>
        </div>

        <div className="bento-grid">
          {/* Large Card: Skincare */}
          <Link to="/category/skincare" className="bento-card bento-large group">
            <span className="bento-tag">Most Popular</span>
            <div>
              <h3 className="font-serif text-3xl font-bold mb-2">Skincare Rituals</h3>
              <p className="text-sm text-muted-fg leading-relaxed">
                Barrier-restoring cleansers, active serums, essences, and hydrating moisturizers.
              </p>
            </div>
            <div className="bento-arrow">↗</div>
          </Link>

          {/* Standard Card 1: Makeup */}
          <Link to="/category/makeup" className="bento-card group">
            <span className="bento-tag">Color Studio</span>
            <div>
              <h3 className="font-serif text-2xl font-bold mb-1">Makeup</h3>
              <p className="text-xs text-muted-fg">Face, eye, and lip color cosmetics.</p>
            </div>
            <div className="bento-arrow">↗</div>
          </Link>

          {/* Standard Card 2: Sun Care */}
          <Link to="/category/sun-care" className="bento-card group">
            <span className="bento-tag">SPF 50+</span>
            <div>
              <h3 className="font-serif text-2xl font-bold mb-1">Sun Care</h3>
              <p className="text-xs text-muted-fg">Daily UV protection creams &amp; sticks.</p>
            </div>
            <div className="bento-arrow">↗</div>
          </Link>

          {/* Wide Card: Hair Care */}
          <Link to="/category/hair-care" className="bento-card bento-wide group">
            <span className="bento-tag">Botanical Care</span>
            <div>
              <h3 className="font-serif text-2xl font-bold mb-1">Hair &amp; Scalp Care</h3>
              <p className="text-xs text-muted-fg">
                Nourishing shampoos, conditioners, and reparative hair masks.
              </p>
            </div>
            <div className="bento-arrow">↗</div>
          </Link>
        </div>
      </section>

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
