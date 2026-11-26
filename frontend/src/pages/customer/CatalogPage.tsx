import React, { useDeferredValue, useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Sparkles, X } from 'lucide-react';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import { Button, Card } from '@/components/common/UI';
import { API_BASE_URL } from '@/utils/apiConfig';

const CATEGORY_EDITORIAL: Record<
  string,
  { eyebrow: string; title: string; subtitle: string; gradient: string }
> = {
  'sun-care': {
    eyebrow: 'Daily UV Defense',
    title: 'Sun Care',
    subtitle:
      'Weightless Korean, Japanese & dermatologist-loved SPF formulas with zero white cast.',
    gradient: 'from-amber-50/90 via-card to-blush/30',
  },
  skincare: {
    eyebrow: 'Barrier & Glass Skin Rituals',
    title: 'Skincare',
    subtitle:
      'Clinically proven actives, snail mucin essences, and ceramide-rich moisturizers.',
    gradient: 'from-emerald-50/70 via-card to-beige/60',
  },
  'hair-care': {
    eyebrow: 'Salon-Grade Gloss & Repair',
    title: 'Hair Care',
    subtitle:
      'Honey-infused oils, molecular bond-building masks, and leave-in treatments.',
    gradient: 'from-amber-50/70 via-card to-beige/70',
  },
  fragrance: {
    eyebrow: 'Haute Parfumerie & Mists',
    title: 'Fragrance',
    subtitle:
      'Iconic niche eau de parfum flacons, warm gourmand mists, and signature florals.',
    gradient: 'from-rose-50/80 via-card to-blush/40',
  },
  'beauty-tools': {
    eyebrow: 'Precision Devices & Brushes',
    title: 'Tools & Brushes',
    subtitle:
      'Pro-grade multi-stylers, microcurrent wands, silk pillowcases, and sculpting stones.',
    gradient: 'from-slate-100/80 via-card to-beige/60',
  },
  makeup: {
    eyebrow: 'Runway Color & Complexion',
    title: 'Makeup',
    subtitle:
      'Viral liquid blushes, blurring setting sprays, lip oils, and velvet matte icons.',
    gradient: 'from-blush/50 via-card to-rose-50/60',
  },
  'body-care': {
    eyebrow: 'Silk-Smooth Body Rituals',
    title: 'Body Care',
    subtitle:
      'Whipped body butters, smoothing AHA washes, and nourishing botanical oils.',
    gradient: 'from-beige/80 via-card to-blush/30',
  },
  'makeup-sets': {
    eyebrow: 'Curated Gift Editions',
    title: 'Makeup & Skincare Sets',
    subtitle:
      'Limited-edition discovery kits, lip vaults, and travel-ready beauty rituals.',
    gradient: 'from-blush/40 via-card to-amber-50/60',
  },
};

export const CatalogPage: React.FC = () => {
  const { categorySlug, brandSlug } = useParams();
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';
  const initialSkinType = searchParams.get('skin_type') || '';
  const initialSort = searchParams.get('sort') || 'newest';

  const [q, setQ] = useState(initialQuery);
  const deferredQ = useDeferredValue(q);
  const [selectedCategory, setSelectedCategory] = useState(categorySlug || '');
  const [selectedBrand, setSelectedBrand] = useState(brandSlug || '');
  const [skinType, setSkinType] = useState(initialSkinType);
  const [shade, setShade] = useState('');
  const deferredShade = useDeferredValue(shade);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [inStockOnly, setInStockOnly] = useState(false);
  const [sort, setSort] = useState(initialSort);
  const [page, setPage] = useState(1);

  useEffect(() => {
    setSelectedCategory(categorySlug || '');
    setSelectedBrand(brandSlug || '');
    setQ(initialQuery);
    setSkinType(initialSkinType);
    setShade('');
    setMinPrice('');
    setMaxPrice('');
    setInStockOnly(false);
    setSort(initialSort);
    setPage(1);
  }, [categorySlug, brandSlug, initialQuery, initialSkinType, initialSort]);

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: catalogApi.getCategories,
  });
  const { data: brands } = useQuery({
    queryKey: ['brands'],
    queryFn: catalogApi.getBrands,
  });

  const activeCategorySlug =
    (categorySlug || selectedCategory).trim().toLowerCase() || undefined;
  const activeBrandSlug = (brandSlug || selectedBrand).trim().toLowerCase() || undefined;

  const activeCategory = categories?.find(
    (c) => c.slug.trim().toLowerCase() === activeCategorySlug
  );
  const activeBrand = brands?.find((b) => b.slug.trim().toLowerCase() === activeBrandSlug);

  const resetFilters = () => {
    setQ('');
    if (!categorySlug) setSelectedCategory('');
    if (!brandSlug) setSelectedBrand('');
    setSkinType('');
    setShade('');
    setMinPrice('');
    setMaxPrice('');
    setInStockOnly(false);
    setSort('newest');
    setPage(1);
  };

  const hasExtraFilters = Boolean(
    q.trim() ||
      (!categorySlug && selectedCategory) ||
      (!brandSlug && selectedBrand) ||
      skinType ||
      shade.trim() ||
      minPrice ||
      maxPrice ||
      inStockOnly
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: [
      'catalog',
      deferredQ,
      activeCategorySlug,
      activeBrandSlug,
      skinType,
      deferredShade,
      minPrice,
      maxPrice,
      inStockOnly,
      sort,
      page,
    ],
    queryFn: () =>
      catalogApi.getProducts({
        q: deferredQ.trim() || undefined,
        category_slug: activeCategorySlug,
        brand_slug: activeBrandSlug,
        skin_type: skinType || undefined,
        shade: deferredShade.trim() || undefined,
        min_price: minPrice ? Number(minPrice) : undefined,
        max_price: maxPrice ? Number(maxPrice) : undefined,
        in_stock: inStockOnly ? true : undefined,
        sort,
        page,
        page_size: 12,
      }),
  });

  return (
    <div className="grid gap-8 lg:grid-cols-[260px_1fr]">
      <aside aria-label="Product filters">
        <Card className="space-y-4">
          <h2 className="font-serif text-xl font-bold">Filter Cosmetics</h2>
          <div>
            <label htmlFor="filter-q" className="block text-xs font-medium text-muted-fg">
              Keyword
            </label>
            <input
              id="filter-q"
              type="text"
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setPage(1);
              }}
              placeholder="Serum, Blush, SPF..."
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
            />
          </div>
          {!categorySlug && (
            <div>
              <label htmlFor="filter-cat" className="block text-xs font-medium text-muted-fg">
                Category
              </label>
              <select
                id="filter-cat"
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setPage(1);
                }}
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm"
              >
                <option value="">All Categories</option>
                {categories?.map((c) => (
                  <option key={c.id} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          )}
          {!brandSlug && (
            <div>
              <label htmlFor="filter-brand" className="block text-xs font-medium text-muted-fg">
                Brand
              </label>
              <select
                id="filter-brand"
                value={selectedBrand}
                onChange={(e) => {
                  setSelectedBrand(e.target.value);
                  setPage(1);
                }}
                className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm"
              >
                <option value="">All Brands</option>
                {brands?.map((b) => (
                  <option key={b.id} value={b.slug}>
                    {b.name}{b.country_of_origin ? ` (${b.country_of_origin})` : ''}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label htmlFor="filter-skin" className="block text-xs font-medium text-muted-fg">
              Skin Type
            </label>
            <select
              id="filter-skin"
              value={skinType}
              onChange={(e) => {
                setSkinType(e.target.value);
                setPage(1);
              }}
              className="mt-1 w-full rounded-lg border border-border bg-card px-3 py-2 text-sm"
            >
              <option value="">Any Skin Type</option>
              <option value="dry">Dry</option>
              <option value="oily">Oily</option>
              <option value="combination">Combination</option>
              <option value="sensitive">Sensitive</option>
              <option value="normal">Normal</option>
            </select>
          </div>
          <div>
            <label htmlFor="filter-shade" className="block text-xs font-medium text-muted-fg">
              Shade / Color
            </label>
            <input
              id="filter-shade"
              type="text"
              value={shade}
              onChange={(e) => {
                setShade(e.target.value);
                setPage(1);
              }}
              placeholder="e.g. Ivory, Red, Joy"
              className="mt-1 w-full rounded-lg border border-border px-3 py-2 text-sm"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="filter-min" className="block text-xs font-medium text-muted-fg">
                Min USD
              </label>
              <input
                id="filter-min"
                type="number"
                min={0}
                value={minPrice}
                onChange={(e) => {
                  setMinPrice(e.target.value);
                  setPage(1);
                }}
                className="mt-1 w-full rounded-lg border border-border px-2 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="filter-max" className="block text-xs font-medium text-muted-fg">
                Max USD
              </label>
              <input
                id="filter-max"
                type="number"
                min={0}
                value={maxPrice}
                onChange={(e) => {
                  setMaxPrice(e.target.value);
                  setPage(1);
                }}
                className="mt-1 w-full rounded-lg border border-border px-2 py-2 text-sm"
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={inStockOnly}
              onChange={(e) => {
                setInStockOnly(e.target.checked);
                setPage(1);
              }}
            />
            <span>In stock only</span>
          </label>
          {hasExtraFilters && (
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={resetFilters}
            >
              Reset Filters
            </Button>
          )}
        </Card>
      </aside>

      <section className="space-y-6">
        {/* Editorial Category Header Banner */}
        {(() => {
          const editorial = activeCategorySlug
            ? CATEGORY_EDITORIAL[activeCategorySlug]
            : undefined;
          const heading =
            editorial?.title ||
            activeCategory?.name ||
            activeBrand?.name ||
            categorySlug?.replace(/-/g, ' ') ||
            brandSlug?.replace(/-/g, ' ') ||
            'Cosmetic Catalog';
          const eyebrow = editorial?.eyebrow || (activeBrand ? 'Brand Atelier' : 'Curated Collection');
          const subtitle =
            editorial?.subtitle ||
            activeCategory?.description ||
            (activeBrand
              ? `Explore authentic best-sellers from ${activeBrand.name}.`
              : 'Authentic luxury makeup, barrier skincare, UV defense, and salon hair rituals.');
          const gradient = editorial?.gradient || 'from-beige/60 via-card to-blush/30';

          return (
            <div
              className={`rounded-3xl border border-border/80 bg-gradient-to-br ${gradient} p-6 shadow-sm sm:p-8`}
            >
              <div className="flex flex-wrap items-end justify-between gap-4">
                <div className="max-w-2xl space-y-2">
                  <p className="inline-flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-widest text-primary">
                    <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
                    {eyebrow}
                  </p>
                  <h1 className="font-serif text-3xl font-bold capitalize text-foreground sm:text-4xl">
                    {heading}
                  </h1>
                  <p className="text-sm text-muted-fg">{subtitle}</p>
                  {!isError && (
                    <p className="pt-1 font-mono text-xs font-medium text-foreground/80">
                      {isLoading ? 'Loading products...' : `${data?.total ?? 0} products available`}
                    </p>
                  )}
                </div>
                <div>
                  <label htmlFor="sort-select" className="mr-2 text-sm text-muted-fg">
                    Sort:
                  </label>
                  <select
                    id="sort-select"
                    value={sort}
                    onChange={(e) => {
                      setSort(e.target.value);
                      setPage(1);
                    }}
                    className="min-h-[44px] rounded-xl border border-border bg-card px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <option value="newest">Newest</option>
                    <option value="price_asc">Price: Low to High</option>
                    <option value="price_desc">Price: High to Low</option>
                    <option value="rating">Top Rated</option>
                  </select>
                </div>
              </div>
            </div>
          );
        })()}

        {/* Quick Category Navigation Tabs across all 6 core categories */}
        <nav aria-label="Browse categories" className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          <Link
            to="/catalog"
            className={`whitespace-nowrap rounded-full px-4 py-2 text-xs font-semibold transition-all ${
              !activeCategorySlug
                ? 'bg-primary text-primary-fg shadow-sm'
                : 'border border-border/80 bg-card text-muted-fg hover:border-primary/40 hover:text-foreground'
            }`}
          >
            All Products
          </Link>
          {[
            { name: 'Makeup', slug: 'makeup' },
            { name: 'Skincare', slug: 'skincare' },
            { name: 'Sun Care', slug: 'sun-care' },
            { name: 'Hair Care', slug: 'hair-care' },
            { name: 'Fragrance', slug: 'fragrance' },
            { name: 'Tools & Brushes', slug: 'beauty-tools' },
          ].map((cat) => {
            const isActive = activeCategorySlug === cat.slug;
            return (
              <Link
                key={cat.slug}
                to={`/category/${cat.slug}`}
                className={`whitespace-nowrap rounded-full px-4 py-2 text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-primary text-primary-fg shadow-sm'
                    : 'border border-border/80 bg-card text-muted-fg hover:border-primary/40 hover:text-foreground'
                }`}
              >
                {cat.name}
              </Link>
            );
          })}
        </nav>

        {/* Interactive Removable Active Filter Chips */}
        {hasExtraFilters && (
          <div className="flex flex-wrap items-center gap-2" aria-label="Active filters">
            {q.trim() && (
              <button
                type="button"
                onClick={() => {
                  setQ('');
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>Keyword: {q.trim()}</span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            {!categorySlug && selectedCategory && (
              <button
                type="button"
                onClick={() => {
                  setSelectedCategory('');
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>Category: {activeCategory?.name || selectedCategory}</span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            {!brandSlug && selectedBrand && (
              <button
                type="button"
                onClick={() => {
                  setSelectedBrand('');
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>Brand: {activeBrand?.name || selectedBrand}</span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            {skinType && (
              <button
                type="button"
                onClick={() => {
                  setSkinType('');
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium capitalize text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>Skin: {skinType}</span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            {shade.trim() && (
              <button
                type="button"
                onClick={() => {
                  setShade('');
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>Shade: {shade.trim()}</span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            {(minPrice || maxPrice) && (
              <button
                type="button"
                onClick={() => {
                  setMinPrice('');
                  setMaxPrice('');
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>
                  Price: {minPrice ? `$${minPrice}` : '$0'} – {maxPrice ? `$${maxPrice}` : 'Any'}
                </span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            {inStockOnly && (
              <button
                type="button"
                onClick={() => {
                  setInStockOnly(false);
                  setPage(1);
                }}
                className="inline-flex items-center gap-1.5 rounded-full border border-primary/25 bg-primary/10 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/20 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <span>In Stock Only</span>
                <X className="h-3.5 w-3.5" aria-hidden="true" />
              </button>
            )}
            <button
              type="button"
              onClick={resetFilters}
              className="px-2 py-1 text-xs font-semibold text-muted-fg underline underline-offset-4 hover:text-foreground"
            >
              Clear all
            </button>
          </div>
        )}

        {isError ? (
          <div role="alert">
            <Card className="border-destructive bg-card p-6">
              <h2 className="font-serif text-lg font-semibold text-destructive">
                Unable to load products right now
              </h2>
              <p className="mt-1 text-sm text-muted-fg">
                {error instanceof Error
                  ? error.message
                  : 'The catalog service could not be reached. Please verify the API connection.'}
              </p>
              <p className="mt-1 font-mono text-xs text-muted-fg">
                API endpoint: {API_BASE_URL}/products
              </p>
              <Button
                type="button"
                variant="outline"
                className="mt-4"
                onClick={() => void refetch()}
              >
                Retry
              </Button>
            </Card>
          </div>
        ) : isLoading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div key={n} className="h-80 animate-pulse rounded-xl bg-beige" />
            ))}
          </div>
        ) : data && data.items.length > 0 ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <h2 className="font-serif text-xl font-semibold text-foreground">
              No matching products found
            </h2>
            <p className="mt-1 text-sm text-muted-fg">
              Try clearing your active filters or browsing another category.
            </p>
            {hasExtraFilters && (
              <Button type="button" variant="outline" className="mt-4" onClick={resetFilters}>
                Clear Filters
              </Button>
            )}
          </Card>
        )}

        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-center gap-3 pt-4">
            <Button
              variant="outline"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <span className="font-mono text-sm">
              Page {data.page} / {data.total_pages}
            </span>
            <Button
              variant="outline"
              disabled={page >= data.total_pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </section>
    </div>
  );
};

