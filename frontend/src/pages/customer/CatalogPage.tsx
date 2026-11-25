import React, { useDeferredValue, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { catalogApi } from '@/services/api';
import { ProductCard } from '@/components/customer/ProductCard';
import { Button, Card } from '@/components/common/UI';

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

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: catalogApi.getCategories,
  });
  const { data: brands } = useQuery({
    queryKey: ['brands'],
    queryFn: catalogApi.getBrands,
  });

  const activeCategorySlug = categorySlug || selectedCategory || undefined;
  const activeBrandSlug = brandSlug || selectedBrand || undefined;

  const { data, isLoading } = useQuery({
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
        q: deferredQ || undefined,
        category_slug: activeCategorySlug,
        brand_slug: activeBrandSlug,
        skin_type: skinType || undefined,
        shade: deferredShade || undefined,
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
                    {b.name}
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
                onChange={(e) => setMinPrice(e.target.value)}
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
                onChange={(e) => setMaxPrice(e.target.value)}
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
        </Card>
      </aside>

      <section className="space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="font-serif text-3xl font-bold capitalize">
              {categorySlug?.replace('-', ' ') || brandSlug?.replace('-', ' ') || 'Cosmetic Catalog'}
            </h1>
            <p className="text-sm text-muted-fg">{data?.total ?? 0} products available</p>
          </div>
          <div>
            <label htmlFor="sort-select" className="mr-2 text-sm text-muted-fg">
              Sort:
            </label>
            <select
              id="sort-select"
              value={sort}
              onChange={(e) => setSort(e.target.value)}
              className="rounded-lg border border-border bg-card px-3 py-2 text-sm"
            >
              <option value="newest">Newest</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="rating">Top Rated</option>
            </select>
          </div>
        </div>

        {isLoading ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div key={n} className="h-80 animate-pulse rounded-xl bg-beige" />
            ))}
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {data?.items.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
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

